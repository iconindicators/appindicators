#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from pathlib import Path
import math, requests


COMET_URL = "https://www.minorplanetcenter.net/iau/Ephemerides/Comets/"
COMET_URL_MPC = COMET_URL + "Soft00Cmt.txt"
COMET_URL_XEPHEM = COMET_URL + "Soft03Cmt.txt"

MINOR_PLANET_URL = "https://minorplanetcenter.net/iau/Ephemerides/"

MINOR_PLANET_BRIGHT_URL_MPC = MINOR_PLANET_URL + "Bright/2018/Soft00Bright.txt"
MINOR_PLANET_BRIGHT_URL_XEPHEM = MINOR_PLANET_URL + "Bright/2018/Soft03Bright.txt"

MINOR_PLANET_CRITICAL_URL_MPC = MINOR_PLANET_URL + "CritList/Soft00CritList.txt"
MINOR_PLANET_CRITICAL_URL_XEPHEM = MINOR_PLANET_URL + "CritList/Soft03CritList.txt"

MINOR_PLANET_DISTANT_URL_MPC = MINOR_PLANET_URL + "Distant/Soft00Distant.txt"
MINOR_PLANET_DISTANT_URL_XEPHEM = MINOR_PLANET_URL + "Distant/Soft03Distant.txt"

MINOR_PLANET_UNUSUAL_URL = MINOR_PLANET_URL + "Unusual/Soft00Unusual.txt"
MINOR_PLANET_UNUSUAL_URL_XEPHEM_FORMAT = MINOR_PLANET_URL + "Unusual/Soft03Unusual.txt"


#TODO Change to reading in an existing file.
def getData( url ):
    filename = Path( url ).name
    if not Path( filename ).exists():
        with open( filename, 'wb' ) as f:
            f.write( requests.get( url ).content )

    with open( filename, 'r' ) as f:
        contents = f.readlines()

    return contents


# https://www.minorplanetcenter.net/iau/info/PackedDates.html
def getUnpackedDate( packedDate ):
    values = [ 'OFFSET ', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V' ]
    packedDatePadded = " " + packedDate # Add extra space for zero offset.

    year = str( values.index( packedDatePadded[ 1 ] ) ) + packedDatePadded[ 2 : 3 + 1 ]

    month = str( values.index( packedDatePadded[ 4 ] ) )
    if len( month ) == 1:
        month = '0' + month

    day = str( values.index( packedDatePadded[ 5 ] ) )
    if len( day ) == 1:
        day = '0' + day

    if len( packedDate ) == 5:
        day += ".0"

    else:
        day += "." + packedDatePadded[ 6 : ]

    return month + '/' + day + '/' + year


# https://minorplanetcenter.net//iau/lists/CometResolution.html
# https://minorplanetcenter.net/iau/info/CometNamingGuidelines.html
# http://www.icq.eps.harvard.edu/cometnames.html
# https://en.wikipedia.org/wiki/Naming_of_comets
# https://slate.com/technology/2013/11/comet-naming-a-quick-guide.html
def getDesignationComet( name ):
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


# https://www.iau.org/public/themes/naming/
# https://minorplanetcenter.net/iau/info/DesDoc.html
# https://minorplanetcenter.net/iau/info/PackedDes.html
def getDesignationMinorPlanet( name ):

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


def checkXephem( line ):
    message = None
    if "****" in line: # https://github.com/skyfielders/python-skyfield/issues/503#issuecomment-745277162
        message = "Asterisks present"

    else:
        line = ( ',' + line ).split( ',' ) # Add extra ',' to offset the zero index.
        name = line[ 1 ]
        designation = getDesignationComet( name )
        if designation == -1:
            message = "Unknown/bad designation"

        elif ( line[ 2 ] == 'e' and len( line[ 12 ] ) == 1 ) or \
             ( line[ 2 ] == 'h' and len( line[ 10 ] ) == 1 ) or \
             ( line[ 2 ] == 'p' and len( line[ 9 ] ) == 1 ): # https://github.com/brandon-rhodes/pyephem/issues/196
            message = "Missing absolute magnitude"

    return message


def checkMPC( line, isComet ):
    message = None
    if "****" in line: # https://github.com/skyfielders/python-skyfield/issues/503#issuecomment-745277162
        message = "Asterisks present"

    else:
        line = ' ' + line # Add ' ' to offset zero index.
        if isComet:
            name = line[ 103 : 158 + 1 ].strip()
            designation = getDesignationComet( name )
            if designation == -1:
                message = "Unknown/bad designation"

            elif len( line[ 92 : 95 + 1 ].strip() ) == 0:
                message = "Missing absolute magnitude"

            elif len( line[ 97 : 100 + 1 ].strip() ) == 0:
                message = "Missing slope parameter"

        else:
            name = line[ 167 : 194 + 1 ].strip()
            designation = getDesignationMinorPlanet( name )
            if designation == -1:
                message = "Unknown/bad designation"

            elif len( line[ 9 : 13 + 1 ].strip() ) == 0:
                message = "Missing absolute magnitude"

            elif len( line[ 15 : 19 + 1 ].strip() ) == 0:
                message = "Missing slope parameter"

            elif len( line[ 93 : 103 + 1 ].strip() ) == 0: # https://github.com/skyfielders/python-skyfield/issues/449#issuecomment-694159517
                message = "Missing semi-major axis"

    return message


# MPC comet format: https://www.minorplanetcenter.net/iau/info/CometOrbitFormat.html
# Ephem comet format: http://www.clearskyinstitute.com/xephem/help/xephem.html#mozTocId215848
def compareComets( cometsMPC, cometsXephem ):

    # Extract XEphem data and verify.
    xephem = { }
    for i in range( 0, len( cometsXephem ) ):
        if cometsXephem[ i ].startswith( "#" ):
            continue

        message = checkXephem( cometsXephem[ i ] )
        if message is not None:
            print( message, cometsXephem[ i ] )
            continue

        line = ( ',' + cometsXephem[ i ] ).split( ',' ) # Add extra ',' to offset the zero index.
        name = line[ 1 ]
        designation = getDesignationComet( name )
        xephem[ designation ] = line

    # Extract MPC data and verify.
    mpc = { }
    for i in range( 0, len( cometsMPC ) ):
        message = checkMPC( cometsMPC[ i ], True )
        if message is not None:
            print( message, cometsMPC[ i ] )
            continue

        line = ' ' + cometsMPC[ i ] # Add ' ' to offset zero index.
        name = line[ 103 : 158 + 1 ].strip()
        designation = getDesignationComet( name )
        mpc[ designation ] = line

    # Check for a body in one data set but absent in the other...
    missing = [ k for k in xephem.keys() if k not in mpc ]
    if missing:    
        print( "Comets in XEphem not in MPC:", missing )

    missing = [ k for k in mpc.keys() if k not in xephem ]
    if missing:
        print( "Comets in MPC not in XEphem:", missing )    

    # Check for mismatch of field values between each data format...
    for k in xephem.keys():
        if k in mpc:
            message = ""
            if xephem[ k ][ 2 ] == 'e':
                if float( xephem[ k ][ 3 ] ) != float( mpc[ k ][ 72 : 79 + 1 ] ):
                    message = "Mismatch of inclination\n"

                if float( xephem[ k ][ 4 ] ) != float( mpc[ k ][ 62 : 69 + 1 ] ):
                    message = "Mismatch of longitude of ascending node\n"

                if float( xephem[ k ][ 5 ] ) != float( mpc[ k ][ 52 : 59 + 1 ] ):
                    message = "Mismatch of argument of perihelion\n"

                if not math.isclose( float( xephem[ k ][ 8 ] ), float( mpc[ k ][ 42 : 49 + 1 ] ), abs_tol = 1e-06 ):
                    message = "Mismatch of eccentricity\n"

                xephemDate = xephem[ k ][ 10 ].split( '/' )
                if not( xephemDate[ 0 ] == mpc[ k ][ 20 : 21 + 1 ] and math.isclose( float( xephemDate[ 1 ] ), float( mpc[ k ][ 23 : 29 + 1 ] ), abs_tol = 1e-03 ) and xephemDate[ 2 ] == mpc[ k ][ 15 : 18 + 1 ] ):
                    message = "Mismatch of epoch date\n"

                if float( xephem[ k ][ 12 ][ 1 : ] ) != float( mpc[ k ][ 92 : 95 + 1 ] ):
                    message = "Mismatch of absolute magnitude\n"

                if float( xephem[ k ][ 13 ] ) != float( mpc[ k ][ 97 : 100 + 1 ] ):
                    message = "Mismatch of slope parameter\n"

            elif xephem[ k ][ 2 ] == 'h':
                xephemDate = xephem[ k ][ 3 ].split( '/' )
                if not( xephemDate[ 0 ] == mpc[ k ][ 20 : 21 + 1 ] and math.isclose( float( xephemDate[ 1 ] ), float( mpc[ k ][ 23 : 29 + 1 ] ), abs_tol = 1e-03 ) and xephemDate[ 2 ] == mpc[ k ][ 15 : 18 + 1 ] ):
                    message = "Mismatch of epoch date\n"

                if float( xephem[ k ][ 4 ] ) != float( mpc[ k ][ 72 : 79 + 1 ] ):
                    message = "Mismatch of inclination\n"

                if float( xephem[ k ][ 5 ] ) != float( mpc[ k ][ 62 : 69 + 1 ] ):
                    message = "Mismatch of longitude of ascending node\n"

                if float( xephem[ k ][ 6 ] ) != float( mpc[ k ][ 52 : 59 + 1 ] ):
                    message = "Mismatch of argument of perihelion\n"

                if not math.isclose( float( xephem[ k ][ 7 ] ), float( mpc[ k ][ 42 : 49 + 1 ] ), abs_tol = 1e-06 ):
                    message = "Mismatch of eccentricity\n"

                if not math.isclose( float( xephem[ k ][ 8 ] ), float( mpc[ k ][ 31 : 39 + 1 ] ), abs_tol = 1e-06 ):
                    message = "Mismatch of perihelion distance\n"

                if float( xephem[ k ][ 10 ] ) != float( mpc[ k ][ 92 : 95 + 1 ] ):
                    message = "Mismatch of absolute magnitude\n"

                if float( xephem[ k ][ 11 ] ) != float( mpc[ k ][ 97 : 100 + 1 ] ):
                    message = "Mismatch of slope parameter\n"

            elif xephem[ k ][ 2 ] == 'p':
                xephemDate = xephem[ k ][ 3 ].split( '/' )
                if not( xephemDate[ 0 ] == mpc[ k ][ 20 : 21 + 1 ] and math.isclose( float( xephemDate[ 1 ] ), float( mpc[ k ][ 23 : 29 + 1 ] ), abs_tol = 1e-03 ) and xephemDate[ 2 ] == mpc[ k ][ 15 : 18 + 1 ] ):
                    message = "Mismatch of epoch date\n"

                if float( xephem[ k ][ 4 ] ) != float( mpc[ k ][ 72 : 79 + 1 ] ):
                    message = "Mismatch of inclination\n"

                if float( xephem[ k ][ 5 ] ) != float( mpc[ k ][ 52 : 59 + 1 ] ):
                    message = "Mismatch of argument of perihelion\n"

                if not math.isclose( float( xephem[ k ][ 6 ] ), float( mpc[ k ][ 31 : 39 + 1 ] ), abs_tol = 1e-06 ):
                    message = "Mismatch of perihelion distance\n"

                if float( xephem[ k ][ 7 ] ) != float( mpc[ k ][ 62 : 69 + 1 ] ):
                    message = "Mismatch of longitude of ascending node\n"

                if float( xephem[ k ][ 9 ] ) != float( mpc[ k ][ 92 : 95 + 1 ] ):
                    message = "Mismatch of absolute magnitude\n"

                if float( xephem[ k ][ 10 ] ) != float( mpc[ k ][ 97 : 100 + 1 ] ):
                    message = "Mismatch of slope parameter\n"

            else:
                print( "Unknown object type for XEphem comet:", xephem[ k ], '\n' )

            if message:
                print( message, xephem[ k ], '\n', mpc[ k ], '\n' )


# MPC minor planet format: https://www.minorplanetcenter.net/iau/info/MPOrbitFormat.html
# Ephem minor planet format: http://www.clearskyinstitute.com/xephem/help/xephem.html#mozTocId215848
def compareMinorPlanets( minorPlanetsMPC, minorPlanetsXephem ):

    # Extract XEphem data and verify.
    xephem = { }
    for i in range( 0, len( minorPlanetsXephem ) ):
        if minorPlanetsXephem[ i ].startswith( "#" ):
            continue

        message = checkXephem( minorPlanetsXephem[ i ] )
        if message is not None:
            print( message, minorPlanetsXephem[ i ] )
            continue

        line = ( ',' + minorPlanetsXephem[ i ] ).split( ',' ) # Add extra ',' to offset the zero index.
        name = line[ 1 ]
        designation = getDesignationMinorPlanet( name )
        xephem[ designation ] = line

    # Extract MPC data and verify.
    mpc = { }
    for i in range( 0, len( minorPlanetsMPC ) ):
        message = checkMPC( minorPlanetsMPC[ i ], False )
        if message is not None:
            print( message, minorPlanetsMPC[ i ] )
            continue

        line = ' ' + minorPlanetsMPC[ i ] # Add ' ' to offset zero index.
        name = line[ 167 : 194 + 1 ].strip()
        designation = getDesignationMinorPlanet( name )
        mpc[ designation ] = line

    # Check for a body in one data set but absent in the other...
    missing = [ k for k in xephem.keys() if k not in mpc ]
    if missing:    
        print( "Minor planets in XEphem not in MPC:", missing )

    missing = [ k for k in mpc.keys() if k not in xephem ]
    if missing:
        print( "Minor planets in MPC not in XEphem:", missing )    

    # Check for mismatch of field values between each data format...
    for k in xephem.keys():
        if k in mpc:
            message = ""
            if not math.isclose( float( xephem[ k ][ 3 ] ), float( mpc[ k ][ 60 : 68 + 1 ] ), abs_tol = 1e-03 ):
                message += "Mismatch of inclination\n"

            if not math.isclose( float( xephem[ k ][ 4 ] ), float( mpc[ k ][ 49 : 57 + 1 ] ), abs_tol = 1e-03 ):
                message += "Mismatch of longitude of ascending node\n"

            if not math.isclose( float( xephem[ k ][ 5 ] ), float( mpc[ k ][ 38 : 46 + 1 ] ), abs_tol = 1e-03 ):
                message += "Mismatch of argument of perihelion\n"

            if not math.isclose( float( xephem[ k ][ 6 ] ), float( mpc[ k ][ 93 : 103 + 1 ] ), abs_tol = 1e-4 ):
                message += "Mismatch of semi-major axis (mean distance)\n"

            if not math.isclose( float( xephem[ k ][ 7 ] ), float( mpc[ k ][ 81 : 91 + 1 ] ), abs_tol = 1e-6 ):
                message += "Mismatch of mean daily motion\n"

            if not math.isclose( float( xephem[ k ][ 8 ][ 1 : ] ), float( mpc[ k ][ 71 : 79 + 1 ] ), abs_tol = 1e-6 ):
                message += "Mismatch of eccentricity\n"

            if not math.isclose( float( xephem[ k ][ 9 ] ), float( mpc[ k ][ 27 : 35 + 1 ] ), abs_tol = 1e-3 ):
                message += "Mismatch of mean anomaly\n"

            if xephem[ k ][ 10 ] != getUnpackedDate( mpc[ k ][ 21 : 25 + 1 ] ):
                message += "Mismatch of epoch date\n"

            if not math.isclose( float( xephem[ k ][ 12 ][ 1 : ] ), float( mpc[ k ][ 9 : 13 + 1 ] ), abs_tol = 1e-2 ):
                message += "Mismatch of absolute magnitude\n"

            if not math.isclose( float( xephem[ k ][ 13 ][ 1 : ] ), float( mpc[ k ][ 15 : 19 + 1 ] ), abs_tol = 1e-2 ):
                message += "Mismatch of slope parameter\n"

            if message:
                print( message, xephem[ k ], '\n', mpc[ k ], '\n' )


# compareComets( getData( COMET_URL_MPC ), getData( COMET_URL_XEPHEM ) )

# compareMinorPlanets( getData( MINOR_PLANET_BRIGHT_URL_MPC ), getData( MINOR_PLANET_BRIGHT_URL_XEPHEM ) )

# compareMinorPlanets( getData( MINOR_PLANET_CRITICAL_URL_MPC ), getData( MINOR_PLANET_CRITICAL_URL_XEPHEM ) )

# compareMinorPlanets( getData( MINOR_PLANET_DISTANT_URL_MPC ), getData( MINOR_PLANET_DISTANT_URL_XEPHEM ) )

# compareMinorPlanets( getData( MINOR_PLANET_UNUSUAL_URL ), getData( MINOR_PLANET_UNUSUAL_URL_XEPHEM_FORMAT ) )