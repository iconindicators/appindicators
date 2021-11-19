#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from pathlib import Path    
import math, requests


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
# MPC comet format: https://minorplanetcenter.net/iau/info/CometOrbitFormat.html
def compareComets( cometsEphem, cometsMPC ):
    ephem = { }
    for i in range( 0, len( cometsEphem ) ):
        if not cometsEphem[ i ].startswith( "#" ):
            firstCommaIndex = cometsEphem[ i ].index( ',' )
            ephem[ cometsEphem[ i ][ 0 : firstCommaIndex ] ] = ',' + cometsEphem[ i ]

    mpc = { }
    for i in range( 0, len( cometsMPC ) ):
        mpc[ cometsMPC[ i ][ 102 : 158 ].strip() ] = ' ' + cometsMPC[ i ]

    print( "Comets in Ephem not in MPC:", [ k for k in ephem.keys() if k not in mpc ] )    

    print( "Comets in MPC not in Ephem:", [ k for k in mpc.keys() if k not in ephem ] )    

    for k in ephem.keys():
        if k in mpc:
            ephemData = ephem[ k ].split( ',' )
            if ephemData[ 2 ] == 'e':
                if float( ephemData[ 3 ] ) != float( mpc[ k ][ 72 : 79 + 1 ] ):
                    print( "Mismatch inclination:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 4 ] ) != float( mpc[ k ][ 62 : 69 + 1 ] ):
                    print( "Mismatch longitude of ascending node:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 5 ] ) != float( mpc[ k ][ 52 : 59 + 1 ] ):
                    print( "Mismatch argument of perihelion:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if not math.isclose( float( ephemData[ 8 ] ), float( mpc[ k ][ 42 : 49 + 1 ] ), abs_tol = 1e-06 ):
                    print( "Mismatch eccentricity:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 12 ][ 1 : ] ) != float( mpc[ k ][ 92 : 95 + 1 ] ):
                    print( "Mismatch argument of absolute magnitude:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 13 ] ) != float( mpc[ k ][ 97 : 100 + 1 ] ):
                    print( "Mismatch argument of slope parameter:", '\n', ephemData, '\n', mpc[ k ], '\n' )

            elif ephemData[ 2 ] == 'h':
                ephemDate = ephemData[ 3 ].split( '/' )
                if not( ephemDate[ 0 ] == mpc[ k ][ 20 : 21 + 1 ] and math.isclose( float( ephemDate[ 1 ] ), float( mpc[ k ][ 23 : 29 + 1 ] ), abs_tol = 1e-03 ) and ephemDate[ 2 ] == mpc[ k ][ 15 : 18 + 1 ] ):
                    print( "Mismatch epoch of perihelion:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 4 ] ) != float( mpc[ k ][ 72 : 79 + 1 ] ):
                    print( "Mismatch inclination:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 5 ] ) != float( mpc[ k ][ 62 : 69 + 1 ] ):
                    print( "Mismatch longitude of ascending node:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 6 ] ) != float( mpc[ k ][ 52 : 59 + 1 ] ):
                    print( "Mismatch argument of perihelion:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if not math.isclose( float( ephemData[ 7 ] ), float( mpc[ k ][ 42 : 49 + 1 ] ), abs_tol = 1e-06 ):
                    print( "Mismatch eccentricity:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if not math.isclose( float( ephemData[ 8 ] ), float( mpc[ k ][ 31 : 39 + 1 ] ), abs_tol = 1e-06 ):
                    print( "Mismatch perihelion distance:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 10 ] ) != float( mpc[ k ][ 92 : 95 + 1 ] ):
                    print( "Mismatch argument of absolute magnitude:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 11 ] ) != float( mpc[ k ][ 97 : 100 + 1 ] ):
                    print( "Mismatch argument of slope parameter:", '\n', ephemData, '\n', mpc[ k ], '\n' )

            elif ephemData[ 2 ] == 'p':
                ephemDate = ephemData[ 3 ].split( '/' )
                if not( ephemDate[ 0 ] == mpc[ k ][ 20 : 21 + 1 ] and math.isclose( float( ephemDate[ 1 ] ), float( mpc[ k ][ 23 : 29 + 1 ] ), abs_tol = 1e-03 ) and ephemDate[ 2 ] == mpc[ k ][ 15 : 18 + 1 ] ):
                    print( "Mismatch epoch of perihelion:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 4 ] ) != float( mpc[ k ][ 72 : 79 + 1 ] ):
                    print( "Mismatch inclination:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 5 ] ) != float( mpc[ k ][ 52 : 59 + 1 ] ):
                    print( "Mismatch argument of perihelion:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if not math.isclose( float( ephemData[ 6 ] ), float( mpc[ k ][ 31 : 39 + 1 ] ), abs_tol = 1e-06 ):
                    print( "Mismatch perihelion distance:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 7 ] ) != float( mpc[ k ][ 62 : 69 + 1 ] ):
                    print( "Mismatch longitude of ascending node:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 9 ] ) != float( mpc[ k ][ 92 : 95 + 1 ] ):
                    print( "Mismatch argument of absolute magnitude:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 10 ] ) != float( mpc[ k ][ 97 : 100 + 1 ] ):
                    print( "Mismatch argument of slope parameter:", '\n', ephemData, '\n', mpc[ k ], '\n' )

            else:
                print( "Unknown object type for Ephem comet:", ephem[ k ], '\n' )


#TODO...!
# Ephem comet format: http://www.clearskyinstitute.com/xephem/help/xephem.html#mozTocId215848
# MPC comet format: https://minorplanetcenter.net/iau/info/CometOrbitFormat.html
def compareMinorPlanets( cometsEphem, cometsMPC ):
    ephem = { }
    for i in range( 0, len( cometsEphem ) ):
        if not cometsEphem[ i ].startswith( "#" ):
            firstCommaIndex = cometsEphem[ i ].index( ',' )
            ephem[ cometsEphem[ i ][ 0 : firstCommaIndex ] ] = ',' + cometsEphem[ i ]

    mpc = { }
    for i in range( 0, len( cometsMPC ) ):
        mpc[ cometsMPC[ i ][ 102 : 158 ].strip() ] = ' ' + cometsMPC[ i ]

    print( "Comets in Ephem not in MPC:", [ k for k in ephem.keys() if k not in mpc ] )    

    print( "Comets in MPC not in Ephem:", [ k for k in mpc.keys() if k not in ephem ] )    

    for k in ephem.keys():
        if k in mpc:
            ephemData = ephem[ k ].split( ',' )
            if ephemData[ 2 ] == 'e':
                if float( ephemData[ 3 ] ) != float( mpc[ k ][ 72 : 79 + 1 ] ):
                    print( "Mismatch inclination:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 4 ] ) != float( mpc[ k ][ 62 : 69 + 1 ] ):
                    print( "Mismatch longitude of ascending node:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 5 ] ) != float( mpc[ k ][ 52 : 59 + 1 ] ):
                    print( "Mismatch argument of perihelion:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if not math.isclose( float( ephemData[ 8 ] ), float( mpc[ k ][ 42 : 49 + 1 ] ), abs_tol = 1e-06 ):
                    print( "Mismatch eccentricity:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 12 ][ 1 : ] ) != float( mpc[ k ][ 92 : 95 + 1 ] ):
                    print( "Mismatch argument of absolute magnitude:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 13 ] ) != float( mpc[ k ][ 97 : 100 + 1 ] ):
                    print( "Mismatch argument of slope parameter:", '\n', ephemData, '\n', mpc[ k ], '\n' )

            elif ephemData[ 2 ] == 'h':
                ephemDate = ephemData[ 3 ].split( '/' )
                if not( ephemDate[ 0 ] == mpc[ k ][ 20 : 21 + 1 ] and math.isclose( float( ephemDate[ 1 ] ), float( mpc[ k ][ 23 : 29 + 1 ] ), abs_tol = 1e-03 ) and ephemDate[ 2 ] == mpc[ k ][ 15 : 18 + 1 ] ):
                    print( "Mismatch epoch of perihelion:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 4 ] ) != float( mpc[ k ][ 72 : 79 + 1 ] ):
                    print( "Mismatch inclination:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 5 ] ) != float( mpc[ k ][ 62 : 69 + 1 ] ):
                    print( "Mismatch longitude of ascending node:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 6 ] ) != float( mpc[ k ][ 52 : 59 + 1 ] ):
                    print( "Mismatch argument of perihelion:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if not math.isclose( float( ephemData[ 7 ] ), float( mpc[ k ][ 42 : 49 + 1 ] ), abs_tol = 1e-06 ):
                    print( "Mismatch eccentricity:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if not math.isclose( float( ephemData[ 8 ] ), float( mpc[ k ][ 31 : 39 + 1 ] ), abs_tol = 1e-06 ):
                    print( "Mismatch perihelion distance:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 10 ] ) != float( mpc[ k ][ 92 : 95 + 1 ] ):
                    print( "Mismatch argument of absolute magnitude:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 11 ] ) != float( mpc[ k ][ 97 : 100 + 1 ] ):
                    print( "Mismatch argument of slope parameter:", '\n', ephemData, '\n', mpc[ k ], '\n' )

            elif ephemData[ 2 ] == 'p':
                ephemDate = ephemData[ 3 ].split( '/' )
                if not( ephemDate[ 0 ] == mpc[ k ][ 20 : 21 + 1 ] and math.isclose( float( ephemDate[ 1 ] ), float( mpc[ k ][ 23 : 29 + 1 ] ), abs_tol = 1e-03 ) and ephemDate[ 2 ] == mpc[ k ][ 15 : 18 + 1 ] ):
                    print( "Mismatch epoch of perihelion:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 4 ] ) != float( mpc[ k ][ 72 : 79 + 1 ] ):
                    print( "Mismatch inclination:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 5 ] ) != float( mpc[ k ][ 52 : 59 + 1 ] ):
                    print( "Mismatch argument of perihelion:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if not math.isclose( float( ephemData[ 6 ] ), float( mpc[ k ][ 31 : 39 + 1 ] ), abs_tol = 1e-06 ):
                    print( "Mismatch perihelion distance:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 7 ] ) != float( mpc[ k ][ 62 : 69 + 1 ] ):
                    print( "Mismatch longitude of ascending node:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 9 ] ) != float( mpc[ k ][ 92 : 95 + 1 ] ):
                    print( "Mismatch argument of absolute magnitude:", '\n', ephemData, '\n', mpc[ k ], '\n' )

                if float( ephemData[ 10 ] ) != float( mpc[ k ][ 97 : 100 + 1 ] ):
                    print( "Mismatch argument of slope parameter:", '\n', ephemData, '\n', mpc[ k ], '\n' )

            else:
                print( "Unknown object type for Ephem comet:", ephem[ k ], '\n' )


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