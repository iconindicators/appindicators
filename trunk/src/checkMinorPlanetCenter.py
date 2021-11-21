#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from pathlib import Path
import math, re, requests


COMET_URL = "https://www.minorplanetcenter.net/iau/Ephemerides/Comets/"
COMET_URL_EPHEM_FORMAT = COMET_URL + "Soft03Cmt.txt"
COMET_URL_MPC_FORMAT = COMET_URL + "Soft00Cmt.txt"

MINOR_PLANET_URL = "https://minorplanetcenter.net/iau/Ephemerides/"

MINOR_PLANET_BRIGHT_URL_EPHEM_FORMAT = MINOR_PLANET_URL + "Bright/2018/Soft03Bright.txt"
MINOR_PLANET_BRIGHT_URL_MPC_FORMAT = MINOR_PLANET_URL + "Bright/2018/Soft00Bright.txt"

MINOR_PLANET_CRITICAL_URL_EPHEM_FORMAT = MINOR_PLANET_URL + "CritList/Soft03CritList.txt"
MINOR_PLANET_CRITICAL_URL_MPC_FORMAT = MINOR_PLANET_URL + "CritList/Soft00CritList.txt"

MINOR_PLANET_DISTANT_URL_EPHEM_FORMAT = MINOR_PLANET_URL + "Distant/Soft03Distant.txt"
MINOR_PLANET_DISTANT_URL_MPC_FORMAT = MINOR_PLANET_URL + "Distant/Soft00Distant.txt"

MINOR_PLANET_UNUSUAL_URL_EPHEM_FORMAT = MINOR_PLANET_URL + "Unusual/Soft03Unusual.txt"
MINOR_PLANET_UNUSUAL_URL_MPC_FORMAT = MINOR_PLANET_URL + "Unusual/Soft00Unusual.txt"


def getData( url ):
    filename = Path( url ).name
    if not Path( filename ).exists():
        with open( filename, 'wb' ) as file:
            file.write( requests.get( url ).content )

    with open( filename, 'r' ) as theFile:
        contents = theFile.readlines()

    return contents


# Ephem comet format: http://www.clearskyinstitute.com/xephem/help/xephem.html#mozTocId215848
# MPC comet format: https://www.minorplanetcenter.net/iau/info/CometOrbitFormat.html
def compareComets( cometsEphem, cometsMPC ):

    # https://minorplanetcenter.net//iau/lists/CometResolution.html
    # https://minorplanetcenter.net/iau/info/CometNamingGuidelines.html
    # http://www.icq.eps.harvard.edu/cometnames.html
    # https://en.wikipedia.org/wiki/Naming_of_comets
    # https://slate.com/technology/2013/11/comet-naming-a-quick-guide.html
    def getDesignation( name ):
        if name[ 0 ].isnumeric():
            # 1P/Halley
            # 332P/Ikeya-Murakami
            # 332P-B/Ikeya-Murakami
            # 332P-C/Ikeya-Murakami
            # 1I/`Oumuamua
            slash = name.find( '/' )
            if slash == -1:
                # Special case for '282P' which is MPC format, whereas the XEphem format is '282P/'.
                designation = name

            else:            
                dash = name[ 0 : slash ].find( '-' )
                if dash == -1:
                    designation = name[ 0 : slash ]

                else:
                    designation = name[ 0 : dash ]

        elif name[ 0 ].isalpha():
            # C/1995 O1 (Hale-Bopp)
            # P/1998 VS24 (LINEAR)
            # P/2011 UA134 (Spacewatch-PANSTARRS)
            # A/2018 V3
            # C/2019 Y4-D (ATLAS)       
            designation = ' '.join( name.split()[ 0 : 2 ] )

        else:
            designation = -1

        return designation


    ephem = { }
    for i in range( 0, len( cometsEphem ) ):
        if not cometsEphem[ i ].startswith( "#" ):
            firstCommaIndex = cometsEphem[ i ].find( ',' )
            name = cometsEphem[ i ][ 0 : firstCommaIndex ]
            designation = getDesignation( name )
            if designation == -1:
                print( "Unknown/bad designation:\n", cometsEphem[ i ] )

            else:
                ephem[ designation ] = ',' + cometsEphem[ i ] # Add extra ',' to offset the zero column.

    mpc = { }
    for i in range( 0, len( cometsMPC ) ):
        name = cometsMPC[ i ][ 102 : 158 ].strip() # Indices are offset by 1.
        designation = getDesignation( name )
        if designation == -1:
            print( "Unknown/bad designation:\n", cometsMPC[ i ] )

        else:
            mpc[ designation ] = ' ' + cometsMPC[ i ] # Add ' ' to align column index with list index.

    print( "Comets in Ephem not in MPC:", [ k for k in ephem.keys() if k not in mpc ] )    

    print( "Comets in MPC not in Ephem:", [ k for k in mpc.keys() if k not in ephem ] )    

    for k in ephem.keys():
        if k in mpc:
            ephemData = ephem[ k ].split( ',' )
            if ephemData[ 2 ] == 'e':
                if float( ephemData[ 3 ] ) != float( mpc[ k ][ 72 : 79 + 1 ] ):
                    print( "Mismatch inclination (XEphem/MPC):", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 4 ] ) != float( mpc[ k ][ 62 : 69 + 1 ] ):
                    print( "Mismatch longitude of ascending node (XEphem/MPC):", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 5 ] ) != float( mpc[ k ][ 52 : 59 + 1 ] ):
                    print( "Mismatch argument of perihelion (XEphem/MPC):", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if not math.isclose( float( ephemData[ 8 ] ), float( mpc[ k ][ 42 : 49 + 1 ] ), abs_tol = 1e-06 ):
                    print( "Mismatch eccentricity (XEphem/MPC):", '\n', ephemData, '\n', mpc[ k ], '\n' )

                ephemDate = ephemData[ 10 ].split( '/' )
                if not( ephemDate[ 0 ] == mpc[ k ][ 20 : 21 + 1 ] and math.isclose( float( ephemDate[ 1 ] ), float( mpc[ k ][ 23 : 29 + 1 ] ), abs_tol = 1e-03 ) and ephemDate[ 2 ] == mpc[ k ][ 15 : 18 + 1 ] ):
                    print( "Mismatch epoch date (XEphem/MPC):", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 12 ][ 1 : ] ) != float( mpc[ k ][ 92 : 95 + 1 ] ):
                    print( "Mismatch argument of absolute magnitude (XEphem/MPC):", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 13 ] ) != float( mpc[ k ][ 97 : 100 + 1 ] ):
                    print( "Mismatch argument of slope parameter (XEphem/MPC):", '\n', ephemData, '\n', mpc[ k ], '\n' )

            elif ephemData[ 2 ] == 'h':
                ephemDate = ephemData[ 3 ].split( '/' )
                if not( ephemDate[ 0 ] == mpc[ k ][ 20 : 21 + 1 ] and math.isclose( float( ephemDate[ 1 ] ), float( mpc[ k ][ 23 : 29 + 1 ] ), abs_tol = 1e-03 ) and ephemDate[ 2 ] == mpc[ k ][ 15 : 18 + 1 ] ):
                    print( "Mismatch epoch date (XEphem/MPC):", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 4 ] ) != float( mpc[ k ][ 72 : 79 + 1 ] ):
                    print( "Mismatch inclination (XEphem/MPC):", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 5 ] ) != float( mpc[ k ][ 62 : 69 + 1 ] ):
                    print( "Mismatch longitude of ascending node (XEphem/MPC):", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 6 ] ) != float( mpc[ k ][ 52 : 59 + 1 ] ):
                    print( "Mismatch argument of perihelion (XEphem/MPC):", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if not math.isclose( float( ephemData[ 7 ] ), float( mpc[ k ][ 42 : 49 + 1 ] ), abs_tol = 1e-06 ):
                    print( "Mismatch eccentricity (XEphem/MPC):", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if not math.isclose( float( ephemData[ 8 ] ), float( mpc[ k ][ 31 : 39 + 1 ] ), abs_tol = 1e-06 ):
                    print( "Mismatch perihelion distance (XEphem/MPC):", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 10 ] ) != float( mpc[ k ][ 92 : 95 + 1 ] ):
                    print( "Mismatch argument of absolute magnitude (XEphem/MPC):", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 11 ] ) != float( mpc[ k ][ 97 : 100 + 1 ] ):
                    print( "Mismatch argument of slope paramete (XEphem/MPC)r:", '\n', ephemData, '\n', mpc[ k ], '\n' )

            elif ephemData[ 2 ] == 'p':
                ephemDate = ephemData[ 3 ].split( '/' )
                if not( ephemDate[ 0 ] == mpc[ k ][ 20 : 21 + 1 ] and math.isclose( float( ephemDate[ 1 ] ), float( mpc[ k ][ 23 : 29 + 1 ] ), abs_tol = 1e-03 ) and ephemDate[ 2 ] == mpc[ k ][ 15 : 18 + 1 ] ):
                    print( "Mismatch epoch date (XEphem/MPC):", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 4 ] ) != float( mpc[ k ][ 72 : 79 + 1 ] ):
                    print( "Mismatch inclination (XEphem/MPC):", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 5 ] ) != float( mpc[ k ][ 52 : 59 + 1 ] ):
                    print( "Mismatch argument of perihelion (XEphem/MPC):", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if not math.isclose( float( ephemData[ 6 ] ), float( mpc[ k ][ 31 : 39 + 1 ] ), abs_tol = 1e-06 ):
                    print( "Mismatch perihelion distance (XEphem/MPC):", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 7 ] ) != float( mpc[ k ][ 62 : 69 + 1 ] ):
                    print( "Mismatch longitude of ascending node (XEphem/MPC):", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 9 ] ) != float( mpc[ k ][ 92 : 95 + 1 ] ):
                    print( "Mismatch argument of absolute magnitude (XEphem/MPC):", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 10 ] ) != float( mpc[ k ][ 97 : 100 + 1 ] ):
                    print( "Mismatch argument of slope parameter (XEphem/MPC):", '\n', ephemData, '\n', mpc[ k ], '\n' )

            else:
                print( "Unknown object type for Ephem comet:", ephem[ k ], '\n' )


# Ephem minor planet format: http://www.clearskyinstitute.com/xephem/help/xephem.html#mozTocId215848
# MPC minor planet format: https://www.minorplanetcenter.net/iau/info/MPOrbitFormat.html
def compareMinorPlanets( minorPlanetsEphem, minorPlanetsMPC ):

    # https://www.iau.org/public/themes/naming/
    # https://minorplanetcenter.net/iau/info/DesDoc.html
    # https://minorplanetcenter.net/iau/info/PackedDes.html
    def getDesignation( name ):

# Ephem examples
# 1 Ceres
#
# 1915 1953 EA
#
# 944 Hidalgo
# 15788 1993 SB
# 1993 RP
#
# 433 Eros
# 3102 Krok
# 7236 1987 PA
# 1979 XB
# 3271 Ul
#
# MPC Examples
# (1) Ceres
#
# (1915)
#
# (944) Hidalgo
# (15788)
# 1993 RP
#
# (433) Eros
# (3102) Krok
# (7236)
# 1979 XB
# (3271) Ul

#TODO Handle pre 1925 discoveries mentioned in above document at bottom of first section.  Need to find an example if possible.
# A904 OA    This is a non-real example...maybe iterate through all minor planets looking for alphanumericnumericnumericspacealphaalpha
#
#TODO Maybe download the MPC database (30MB) and look inside...is it just minor planets, or comets too?
        # components = name.split( ' ' ) #TODO Try without the ' ' below...
        components = name.split()
        components[ 0 ] = components[ 0 ].strip( '(' ).strip( ')' )

        isProvisionalDesignation = \
            len( components ) == 2 and \
            len( components[ 0 ] ) == 4 and components[ 0 ].isnumeric() and \
            ( ( len( components[ 1 ] ) == 2 and components[ 1 ].isalpha() and components[ 1 ].isupper() ) or \
              ( len( components[ 1 ] ) > 2 and components[ 1 ][ 0 : 2 ].isalpha() and components[ 1 ][ 0 : 2 ].isupper() and components[ 1 ][ 2 : ].isnumeric() ) )

        if isProvisionalDesignation:
            designation = name

        else:
            designation = components[ 0 ]

        return designation


    ephem = { }
    for i in range( 0, len( minorPlanetsEphem ) ):
        if not minorPlanetsEphem[ i ].startswith( "#" ):
            firstCommaIndex = minorPlanetsEphem[ i ].find( ',' )
            name = minorPlanetsEphem[ i ][ 0 : firstCommaIndex ]
            if '/' in name: print( name )
            designation = getDesignation( name )
            if designation == -1:
                print( "Unknown/bad designation:\n", minorPlanetsEphem[ i ] )

            else:
                ephem[ designation ] = ',' + minorPlanetsEphem[ i ] # Add extra ',' to offset the zero column.

    mpc = { }
    for i in range( 0, len( minorPlanetsMPC ) ):
        name = minorPlanetsMPC[ i ][ 166 : 194 ].strip() # Indices are offset by 1.
        if '/' in name: print( name )
        designation = getDesignation( name )
        if designation == -1:
            print( "Unknown/bad designation:\n", minorPlanetsMPC[ i ] )

        else:
            mpc[ designation ] = ' ' + minorPlanetsMPC[ i ] # Add ' ' to align column index with list index.

    print( "Comets in Ephem not in MPC:", [ k for k in ephem.keys() if k not in mpc ] )    
    
    print( "Comets in MPC not in Ephem:", [ k for k in mpc.keys() if k not in ephem ] )    
    
    # for k in ephem.keys():
    #     print( ephem[ k ].split( ',' )[ 2 ] )
    
    
    # for k in ephem.keys():
    #     if k in mpc:
    #         ephemData = ephem[ k ].split( ',' )
    #         if ephemData[ 2 ] == 'e':
    #             if float( ephemData[ 3 ] ) != float( mpc[ k ][ 72 : 79 + 1 ] ):
    #                 print( "Mismatch inclination:", '\n', ephemData, '\n', mpc[ k ], '\n' )
    #
    #             if float( ephemData[ 4 ] ) != float( mpc[ k ][ 62 : 69 + 1 ] ):
    #                 print( "Mismatch longitude of ascending node:", '\n', ephemData, '\n', mpc[ k ], '\n' )
    #
    #             if float( ephemData[ 5 ] ) != float( mpc[ k ][ 52 : 59 + 1 ] ):
    #                 print( "Mismatch argument of perihelion:", '\n', ephemData, '\n', mpc[ k ], '\n' )
    #
    #             if not math.isclose( float( ephemData[ 8 ] ), float( mpc[ k ][ 42 : 49 + 1 ] ), abs_tol = 1e-06 ):
    #                 print( "Mismatch eccentricity:", '\n', ephemData, '\n', mpc[ k ], '\n' )
    #
    #             if float( ephemData[ 12 ][ 1 : ] ) != float( mpc[ k ][ 92 : 95 + 1 ] ):
    #                 print( "Mismatch argument of absolute magnitude:", '\n', ephemData, '\n', mpc[ k ], '\n' )
    #
    #             if float( ephemData[ 13 ] ) != float( mpc[ k ][ 97 : 100 + 1 ] ):
    #                 print( "Mismatch argument of slope parameter:", '\n', ephemData, '\n', mpc[ k ], '\n' )
    #
    #         elif ephemData[ 2 ] == 'h':
    #             ephemDate = ephemData[ 3 ].split( '/' )
    #             if not( ephemDate[ 0 ] == mpc[ k ][ 20 : 21 + 1 ] and math.isclose( float( ephemDate[ 1 ] ), float( mpc[ k ][ 23 : 29 + 1 ] ), abs_tol = 1e-03 ) and ephemDate[ 2 ] == mpc[ k ][ 15 : 18 + 1 ] ):
    #                 print( "Mismatch epoch of perihelion:", '\n', ephemData, '\n', mpc[ k ], '\n' )
    #
    #             if float( ephemData[ 4 ] ) != float( mpc[ k ][ 72 : 79 + 1 ] ):
    #                 print( "Mismatch inclination:", '\n', ephemData, '\n', mpc[ k ], '\n' )
    #
    #             if float( ephemData[ 5 ] ) != float( mpc[ k ][ 62 : 69 + 1 ] ):
    #                 print( "Mismatch longitude of ascending node:", '\n', ephemData, '\n', mpc[ k ], '\n' )
    #
    #             if float( ephemData[ 6 ] ) != float( mpc[ k ][ 52 : 59 + 1 ] ):
    #                 print( "Mismatch argument of perihelion:", '\n', ephemData, '\n', mpc[ k ], '\n' )
    #
    #             if not math.isclose( float( ephemData[ 7 ] ), float( mpc[ k ][ 42 : 49 + 1 ] ), abs_tol = 1e-06 ):
    #                 print( "Mismatch eccentricity:", '\n', ephemData, '\n', mpc[ k ], '\n' )
    #
    #             if not math.isclose( float( ephemData[ 8 ] ), float( mpc[ k ][ 31 : 39 + 1 ] ), abs_tol = 1e-06 ):
    #                 print( "Mismatch perihelion distance:", '\n', ephemData, '\n', mpc[ k ], '\n' )
    #
    #             if float( ephemData[ 10 ] ) != float( mpc[ k ][ 92 : 95 + 1 ] ):
    #                 print( "Mismatch argument of absolute magnitude:", '\n', ephemData, '\n', mpc[ k ], '\n' )
    #
    #             if float( ephemData[ 11 ] ) != float( mpc[ k ][ 97 : 100 + 1 ] ):
    #                 print( "Mismatch argument of slope parameter:", '\n', ephemData, '\n', mpc[ k ], '\n' )
    #
    #         elif ephemData[ 2 ] == 'p':
    #             ephemDate = ephemData[ 3 ].split( '/' )
    #             if not( ephemDate[ 0 ] == mpc[ k ][ 20 : 21 + 1 ] and math.isclose( float( ephemDate[ 1 ] ), float( mpc[ k ][ 23 : 29 + 1 ] ), abs_tol = 1e-03 ) and ephemDate[ 2 ] == mpc[ k ][ 15 : 18 + 1 ] ):
    #                 print( "Mismatch epoch of perihelion:", '\n', ephemData, '\n', mpc[ k ], '\n' )
    #
    #             if float( ephemData[ 4 ] ) != float( mpc[ k ][ 72 : 79 + 1 ] ):
    #                 print( "Mismatch inclination:", '\n', ephemData, '\n', mpc[ k ], '\n' )
    #
    #             if float( ephemData[ 5 ] ) != float( mpc[ k ][ 52 : 59 + 1 ] ):
    #                 print( "Mismatch argument of perihelion:", '\n', ephemData, '\n', mpc[ k ], '\n' )
    #
    #             if not math.isclose( float( ephemData[ 6 ] ), float( mpc[ k ][ 31 : 39 + 1 ] ), abs_tol = 1e-06 ):
    #                 print( "Mismatch perihelion distance:", '\n', ephemData, '\n', mpc[ k ], '\n' )
    #
    #             if float( ephemData[ 7 ] ) != float( mpc[ k ][ 62 : 69 + 1 ] ):
    #                 print( "Mismatch longitude of ascending node:", '\n', ephemData, '\n', mpc[ k ], '\n' )
    #
    #             if float( ephemData[ 9 ] ) != float( mpc[ k ][ 92 : 95 + 1 ] ):
    #                 print( "Mismatch argument of absolute magnitude:", '\n', ephemData, '\n', mpc[ k ], '\n' )
    #
    #             if float( ephemData[ 10 ] ) != float( mpc[ k ][ 97 : 100 + 1 ] ):
    #                 print( "Mismatch argument of slope parameter:", '\n', ephemData, '\n', mpc[ k ], '\n' )
    #
    #         else:
    #             print( "Unknown object type for Ephem comet:", ephem[ k ], '\n' )


compareComets(
    getData( COMET_URL_EPHEM_FORMAT ),
    getData( COMET_URL_MPC_FORMAT ) )

compareMinorPlanets(
    getData( MINOR_PLANET_BRIGHT_URL_EPHEM_FORMAT ),
    getData( MINOR_PLANET_BRIGHT_URL_MPC_FORMAT ) )


compareMinorPlanets(
    getData( MINOR_PLANET_CRITICAL_URL_EPHEM_FORMAT ),
    getData( MINOR_PLANET_CRITICAL_URL_MPC_FORMAT ) )


compareMinorPlanets(
    getData( MINOR_PLANET_DISTANT_URL_EPHEM_FORMAT ),
    getData( MINOR_PLANET_DISTANT_URL_MPC_FORMAT ) )


compareMinorPlanets(
    getData( MINOR_PLANET_UNUSUAL_URL_EPHEM_FORMAT ),
    getData( MINOR_PLANET_UNUSUAL_URL_MPC_FORMAT ) )
