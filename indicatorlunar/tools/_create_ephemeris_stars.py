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
Backend which creates the list of stars for astrobase and
the star ephemerides for astropyephem and astroskyfield.

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


#TODO What to do about Minkar?
# Does not appear in the IAU list of stars, so leave out
#
#TODO 
# https://github.com/brandon-rhodes/pyephem/issues/289
# Until resolved, leave out Albireo as it is incorrect,
# and also leave out Albereo because not part of PyEphem.
# When resolved, add Albereo back in.

# Given the list of PyEphem supported stars
#   https://github.com/brandon-rhodes/pyephem/blob/master/ephem/stars.py
# there are duplicates and misspellings which must be kept in support of
# previous versions.
#
# Match these stars against the official names from the IAU Catalog
#   http://www.pas.rochester.edu/~emamajek/WGSN/IAU-CSN.txt
# to create the list of stars below, with corresponding HIP, which contains
# only corrected star names (no duplicates) which correlate to those stars
# in PyEphem.
NAMES_TO_HIPS = {
    "ACAMAR"         :  13847,
    "ACHERNAR"       :  7588,
    "ACRUX"          :  60718,
    "ADHARA"         :  33579,
    "ALCOR"          :  65477,
    "ALCYONE"        :  17702,
    "ALDEBARAN"      :  21421,
    "ALDERAMIN"      :  105199,
    "ALFIRK"         :  106032,
    "ALGENIB"        :  1067,
    "ALGIEBA"        :  50583,
    "ALGOL"          :  14576,
    "ALHENA"         :  31681,
    "ALIOTH"         :  62956,
    "ALKAID"         :  67301,
    "ALMACH"         :  9640,
    "ALNAIR"         :  109268,
    "ALNILAM"        :  26311,
    "ALNITAK"        :  26727,
    "ALPHARD"        :  46390,
    "ALPHECCA"       :  76267,
    "ALPHERATZ"      :  677,
    "ALSHAIN"        :  98036,
    "ALTAIR"         :  97649,
    "ANKAA"          :  2081,
    "ANTARES"        :  80763,
    "ARCTURUS"       :  69673,
    "ARKAB POSTERIOR":  95294,
    "ARKAB PRIOR"    :  95241,
    "ARNEB"          :  25985,
    "ATLAS"          :  17847,
    "ATRIA"          :  82273,
    "AVIOR"          :  41037,
    "BELLATRIX"      :  25336,
    "BETELGEUSE"     :  27989,
    "CANOPUS"        :  30438,
    "CAPELLA"        :  24608,
    "CAPH"           :  746,
    "CASTOR"         :  36850,
    "CEBALRAI"       :  86742,
    "DENEB"          :  102098,
    "DENEBOLA"       :  57632,
    "DIPHDA"         :  3419,
    "DUBHE"          :  54061,
    "ELECTRA"        :  17499,
    "ELNATH"         :  25428,
    "ELTANIN"        :  87833,
    "ENIF"           :  107315,
    "FOMALHAUT"      :  113368,
    "GACRUX"         :  61084,
    "GIENAH"         :  59803,
    "HADAR"          :  68702,
    "HAMAL"          :  9884,
    "IZAR"           :  72105,
    "KAUS AUSTRALIS" :  90185,
    "KOCHAB"         :  72607,
    "MAIA"           :  17573,
    "MARKAB"         :  113963,
    "MEGREZ"         :  59774,
    "MENKALINAN"     :  28360,
    "MENKAR"         :  14135,
    "MENKENT"        :  68933,
    "MERAK"          :  53910,
    "MEROPE"         :  17608,
    "MIAPLACIDUS"    :  45238,
    "MIMOSA"         :  62434,
    "MINTAKA"        :  25930,
    "MIRACH"         :  5447,
    "MIRFAK"         :  15863,
    "MIRZAM"         :  30324,
    "MIZAR"          :  65378,
    "NAOS"           :  39429,
    "NIHAL"          :  25606,
    "NUNKI"          :  92855,
    "PEACOCK"        :  100751,
    "PHECDA"         :  58001,
    "POLARIS"        :  11767,
    "POLLUX"         :  37826,
    "PROCYON"        :  37279,
    "RASALGETHI"     :  84345,
    "RASALHAGUE"     :  86032,
    "REGULUS"        :  49669,
    "RIGEL"          :  24436,
    "RIGIL KENTAURUS":  71683,
    "RUKBAT"         :  95347,
    "SABIK"          :  84012,
    "SADALMELIK"     :  109074,
    "SADR"           :  100453,
    "SAIPH"          :  27366,
    "SCHEAT"         :  113881,
    "SCHEDAR"        :  3179,
    "SHAULA"         :  85927,
    "SHELIAK"        :  92420,
    "SIRIUS"         :  32349,
    "SPICA"          :  65474,
    "SUHAIL"         :  44816,
    "SULAFAT"        :  93194,
    "TARAZED"        :  97278,
    "TAYGETA"        :  17531,
    "THUBAN"         :  68756,
    "UNUKALHAI"      :  77070,
    "VEGA"           :  91262,
    "VINDEMIATRIX"   :  63608,
    "WEZEN"          :  34444,
    "ZAURAK"         :  18543,
    "ZUBENELGENUBI"  :  72622 }


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



#TODO Maybe change name...or need additional API?
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


#TODO Maybe this all goes?
# #TODO Best to rename this to something other than create...
# # Maybe initialise or something else?
# # Also rename this file/module AND the calling module.
# def create_ephemeris_stars(
#     output_filename_for_skyfield_star_ephemeris,
#     planet_ephemeris,
#     star_ephemeris,
#     iau_catalog_file ):
#
#     names_to_hips = _get_names_to_hips( iau_catalog_file )
#
#     _print_formatted_stars( names_to_hips )
#
#     _create_ephemeris_skyfield(
#         output_filename_for_skyfield_star_ephemeris,
#         star_ephemeris,
#         list( names_to_hips.values() ) )
#
#     _print_ephemeris_pyephem(
#         planet_ephemeris,
#         star_ephemeris,
#         names_to_hips )
