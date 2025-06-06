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
Create a star ephemeris for use in both PyEphem and Skyfield,
using stars from PyEphem, keeping only those present in the
IAU CSN Catalog with accompanying HIP and absolute magnitude.

WILL NOT WORK ON 32 BIT!!!    TODO Check this...might work on the VM...but not laptop...!
'''


import argparse
import csv
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


def _get_stars_and_hips( iau_catalog_file ):
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


def _get_hips_to_names( iau_catalog_file ):
    stars_from_pyephem = stars.stars.keys()
    hips_to_names = { }
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

                        hips_to_names[ str( hip ) ] = name_utf8

                except ValueError:
                    pass

    return hips_to_names


def _get_names_to_hips( iau_catalog_file ):
    '''
    Reads the IAU Catalog of Star Names (IAU-CSN) and returns a dictionary:
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
    stars_and_hips_ ):

    print( f"List of stars for AstroBase:" )
    for name, hip in stars_and_hips_:
        spacing_name = ' ' * ( IAUCSN_NAME_END - IAUCSN_NAME_START - len( name ) - 1 )
        spacing_hip = ' ' * ( IAUCSN_HIP_END - IAUCSN_HIP_START - len( str( hip ) ) + 1 )
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
    stars_and_hips_ ):

    print( f"Creating { out_file } for Skyfield..." )
    hipparcos_identifiers = (
        [ star_and_hip[ 1 ] for star_and_hip in stars_and_hips_ ] )

    with load.open( star_ephemeris, "rb" ) as in_file, open( out_file, "wb" ) as f:
        for line in in_file:
            # HIP is located at bytes 9 - 14
            #    http://cdsarc.u-strasbg.fr/ftp/cats/I/239/ReadMe
            hip = int( line.decode()[ 9 - 1 : 14 - 1 + 1 ].strip() )
            if hip in hipparcos_identifiers:
                f.write( line )

    print( "Done" )


#TODO Keep?
def _print_ephemeris_pyephemORIG(
    star_information,
    star_ephemeris,
    planet_ephemeris ): 
    '''
    Mostly taken from
        https://github.com/brandon-rhodes/pyephem/blob/master/bin/rebuild-star-data
    '''
    print( "Ephemeris for PyEphem..." )

    hipparcos_dialect = "hipparcos_main_catalog"
    csv.register_dialect(
        hipparcos_dialect,
        delimiter = '|',
        quoting = csv.QUOTE_NONE )

    HIPPARCOS_HIP = 1
    HIPPARCOS_RA_HMS = 3
    HIPPARCOS_DE_DMS = 4
    HIPPARCOS_V_MAG = 5
    HIPPARCOS_PM_RA = 12
    HIPPARCOS_PM_DEC = 13
    HIPPARCOS_SP_TYPE = 76

    hips_to_names = _get_hips_to_names( star_information )
    hips = list( hips_to_names.keys() )
    sun_at = load( planet_ephemeris )[ "Sun" ].at( load.timescale().J( 2000.0 ) )
    results = [ ]
    with open( star_ephemeris, newline = '' ) as f:
        reader = csv.reader( f, hipparcos_dialect )
        for row in reader:
            hip = row[ HIPPARCOS_HIP ].strip()
            if hip in hips:
                right_ascension = ( [
                    float( x )
                    for x in row[ HIPPARCOS_RA_HMS ].split() ] )

                declination = ( [
                    float( x )
                    for x in row[ HIPPARCOS_DE_DMS ].split() ] )

                star = (
                    Star(
                        ra_hours = tuple( right_ascension ),
                        dec_degrees = tuple( declination ),
                        ra_mas_per_year = float( row[ HIPPARCOS_PM_RA ].strip() ),
                        dec_mas_per_year = float( row[ HIPPARCOS_PM_DEC ].strip() ) ) )

                right_ascension, declination, _ = sun_at.observe( star ).radec()

                spectral_type = row[ HIPPARCOS_SP_TYPE ].strip()
                if isinstance( spectral_type, str ):
                    spectral_type = spectral_type[ : 2 ]

                else:
                    spectral_type = "  "
                    # Is NaN; to fix, set to two blank characters (see _libastro.c).

                name = hips_to_names[ hip ].upper()

                components = [
                    name,
                    "f|S|" +
                    spectral_type,
                    f"{right_ascension.hours:.8f}|{ star.ra_mas_per_year }",
                    f"{declination.degrees:.8f}|{ star.dec_mas_per_year }",
                    float( row[ HIPPARCOS_V_MAG ] ),
                ]

                # print( ','.join( str( item ) for item in components ) )
                # print()

                # line = ','.join( str( item ) for item in components )
                # print( f"        \"{ name }\" :" )
                # print( f"            \"{ line }\"," )

                line = ','.join( str( item ) for item in components )
                results.append(
                    f"        \"{ name }\" :\n            \"{ line }\"," )

    results.sort()
    print( *results, sep = '\n' )
    print( "Done" )


def _print_ephemeris_pyephem(
    star_information,
    star_ephemeris,
    planet_ephemeris ): 
    '''
    Mostly taken from
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

    names_to_hips = _get_names_to_hips( star_information )
    names = list( names_to_hips.keys() )

    timescale = load.timescale().J( 2000.0 )
    sun_at = load( planet_ephemeris )[ "Sun" ].at( timescale )
    results = [ ]
    for name in sorted( names):
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
    print( *results, sep = '\n' )
    print( "Done" )


def _create_ephemeris_stars(
        output_filename_for_skyfield_star_ephemeris,
        planet_ephemeris,
        star_ephemeris,
        star_information ):

    stars_and_hips = _get_stars_and_hips( star_information )
    _print_formatted_stars( stars_and_hips )
    _create_ephemeris_skyfield(
        output_filename_for_skyfield_star_ephemeris,
        star_ephemeris,
        stars_and_hips )

    _print_ephemeris_pyephem(
        planet_ephemeris,
        star_ephemeris,
        stars_and_hips )


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

            WILL NOT WORK ON 32 BIT!!!
            ''' ) )

    parser = (
        argparse.ArgumentParser(
            formatter_class = argparse.RawDescriptionHelpFormatter,
            description = description ) )

    parser.add_argument(
        "star_information",
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

#     args = parser.parse_args()
#
#     command = (
#         "python3 -c \"import create_ephemeris_stars; "
#         f"create_ephemeris_stars._create_ephemeris_stars( "
#         f"\\\"{ args.output_filename_for_skyfield_star_ephemeris }\\\", "
#         f"\\\"{ args.planet_ephemeris }\\\", "
#         f"\\\"{ args.star_ephemeris }\\\", "
#         f"\\\"{ args.star_information }\\\" )\"" )
#
#     IndicatorBase.run_python_command_in_virtual_environment(
#         IndicatorBase.VENV_INSTALL,
#         command,
#         "ephem",
#         "pandas",   #TODO Why need pandas?  Needed for read_csv() so is there an equivalent?
# # I don't want to release this script to the end-user only to have them need to install pandas.        
#         "skyfield" )

    star_information = "../../../IndicatorLunarData/IAU-CSN.txt"
    star_ephemeris = "../../../IndicatorLunarData/hip_main.dat"
    planet_ephemeris = "../../../IndicatorLunarData/de421.bsp" 

    _print_ephemeris_pyephem( star_information, star_ephemeris, planet_ephemeris )
