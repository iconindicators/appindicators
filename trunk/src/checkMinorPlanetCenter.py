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


def getData( url ):
    filename = Path( url ).name
    if not Path( filename ).exists():
        with open( filename, 'wb' ) as file:
            file.write( requests.get( url ).content )

    with open( filename, 'r' ) as theFile:
        contents = theFile.readlines()

    return contents


def checkXephem( data ):
    for i in range( 0, len( data ) ):
        if not data[ i ].startswith( "#" ):
            line = ( ',' + data[ i ] ).split( ',' ) # Add extra ',' to offset the zero column.
            message = ""
            if "****" in line: # https://github.com/skyfielders/python-skyfield/issues/503#issuecomment-745277162
                message += "Asterisks present\n"

            if ( line[ 2 ] == 'e' and len( line[ 12 ] ) == 1 ) or \
               ( line[ 2 ] == 'h' and len( line[ 10 ] ) == 1 ) or \
               ( line[ 2 ] == 'p' and len( line[ 9 ] ) == 1 ): # https://github.com/brandon-rhodes/pyephem/issues/196
                message += "Missing absolute magnitude\n"

            if message:
                print( message, line )


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


# Ephem comet format: http://www.clearskyinstitute.com/xephem/help/xephem.html#mozTocId215848
# MPC comet format: https://www.minorplanetcenter.net/iau/info/CometOrbitFormat.html
def compareComets( cometsMPC, cometsXephem ):
    xephem = { }
    for i in range( 0, len( cometsXephem ) ):
        if not cometsXephem[ i ].startswith( "#" ):
            firstCommaIndex = cometsXephem[ i ].find( ',' )
            name = cometsXephem[ i ][ 0 : firstCommaIndex ]
            designation = getDesignationComet( name )
            if designation == -1:
                print( "Unknown/bad designation:\n", cometsXephem[ i ] )

            else:
                xephem[ designation ] = ',' + cometsXephem[ i ] # Add extra ',' to offset the zero column.

    mpc = { }
    for i in range( 0, len( cometsMPC ) ):
        name = cometsMPC[ i ][ 102 : 158 ].strip() # Indices are offset by 1.
        designation = getDesignationComet( name )
        if designation == -1:
            print( "Unknown/bad designation:\n", cometsMPC[ i ] )

        else:
            mpc[ designation ] = ' ' + cometsMPC[ i ] # Add ' ' to align column index with list index.

    missing = [ k for k in xephem.keys() if k not in mpc ]
    if missing:    
        print( "Comets in XEphem not in MPC:", missing )

    missing = [ k for k in mpc.keys() if k not in xephem ]
    if missing:
        print( "Comets in MPC not in XEphem:", missing )    

    for k in xephem.keys():
        if k in mpc:
            xephemData = xephem[ k ].split( ',' )
            message = ""
            if xephemData[ 2 ] == 'e':
                if float( xephemData[ 3 ] ) != float( mpc[ k ][ 72 : 79 + 1 ] ):
                    message = "Mismatch of inclination\n"

                if float( xephemData[ 4 ] ) != float( mpc[ k ][ 62 : 69 + 1 ] ):
                    message = "Mismatch of longitude of ascending node\n"

                if float( xephemData[ 5 ] ) != float( mpc[ k ][ 52 : 59 + 1 ] ):
                    message = "Mismatch of argument of perihelion\n"

                if not math.isclose( float( xephemData[ 8 ] ), float( mpc[ k ][ 42 : 49 + 1 ] ), abs_tol = 1e-06 ):
                    message = "Mismatch of eccentricity\n"

                xephemDate = xephemData[ 10 ].split( '/' )
                if not( xephemDate[ 0 ] == mpc[ k ][ 20 : 21 + 1 ] and math.isclose( float( xephemDate[ 1 ] ), float( mpc[ k ][ 23 : 29 + 1 ] ), abs_tol = 1e-03 ) and xephemDate[ 2 ] == mpc[ k ][ 15 : 18 + 1 ] ):
                    message = "Mismatch of epoch date\n"

                if float( xephemData[ 12 ][ 1 : ] ) != float( mpc[ k ][ 92 : 95 + 1 ] ):
                    message = "Mismatch of absolute magnitude\n"

                if float( xephemData[ 13 ] ) != float( mpc[ k ][ 97 : 100 + 1 ] ):
                    message = "Mismatch of slope parameter\n"

            elif xephemData[ 2 ] == 'h':
                xephemDate = xephemData[ 3 ].split( '/' )
                if not( xephemDate[ 0 ] == mpc[ k ][ 20 : 21 + 1 ] and math.isclose( float( xephemDate[ 1 ] ), float( mpc[ k ][ 23 : 29 + 1 ] ), abs_tol = 1e-03 ) and xephemDate[ 2 ] == mpc[ k ][ 15 : 18 + 1 ] ):
                    message = "Mismatch of epoch date\n"

                if float( xephemData[ 4 ] ) != float( mpc[ k ][ 72 : 79 + 1 ] ):
                    message = "Mismatch of inclination\n"

                if float( xephemData[ 5 ] ) != float( mpc[ k ][ 62 : 69 + 1 ] ):
                    message = "Mismatch of longitude of ascending node\n"

                if float( xephemData[ 6 ] ) != float( mpc[ k ][ 52 : 59 + 1 ] ):
                    message = "Mismatch of argument of perihelion\n"

                if not math.isclose( float( xephemData[ 7 ] ), float( mpc[ k ][ 42 : 49 + 1 ] ), abs_tol = 1e-06 ):
                    message = "Mismatch of eccentricity\n"

                if not math.isclose( float( xephemData[ 8 ] ), float( mpc[ k ][ 31 : 39 + 1 ] ), abs_tol = 1e-06 ):
                    message = "Mismatch of perihelion distance\n"

                if float( xephemData[ 10 ] ) != float( mpc[ k ][ 92 : 95 + 1 ] ):
                    message = "Mismatch of absolute magnitude\n"

                if float( xephemData[ 11 ] ) != float( mpc[ k ][ 97 : 100 + 1 ] ):
                    message = "Mismatch of slope parameter\n"

            elif xephemData[ 2 ] == 'p':
                xephemDate = xephemData[ 3 ].split( '/' )
                if not( xephemDate[ 0 ] == mpc[ k ][ 20 : 21 + 1 ] and math.isclose( float( xephemDate[ 1 ] ), float( mpc[ k ][ 23 : 29 + 1 ] ), abs_tol = 1e-03 ) and xephemDate[ 2 ] == mpc[ k ][ 15 : 18 + 1 ] ):
                    message = "Mismatch of epoch date\n"

                if float( xephemData[ 4 ] ) != float( mpc[ k ][ 72 : 79 + 1 ] ):
                    message = "Mismatch of inclination\n"

                if float( xephemData[ 5 ] ) != float( mpc[ k ][ 52 : 59 + 1 ] ):
                    message = "Mismatch of argument of perihelion\n"

                if not math.isclose( float( xephemData[ 6 ] ), float( mpc[ k ][ 31 : 39 + 1 ] ), abs_tol = 1e-06 ):
                    message = "Mismatch of perihelion distance\n"

                if float( xephemData[ 7 ] ) != float( mpc[ k ][ 62 : 69 + 1 ] ):
                    message = "Mismatch of longitude of ascending node\n"

                if float( xephemData[ 9 ] ) != float( mpc[ k ][ 92 : 95 + 1 ] ):
                    message = "Mismatch of absolute magnitude\n"

                if float( xephemData[ 10 ] ) != float( mpc[ k ][ 97 : 100 + 1 ] ):
                    message = "Mismatch of slope parameter\n"

            else:
                print( "Unknown object type for XEphem comet:", xephem[ k ], '\n' )

            if message:
                print( message, xephemData, '\n', mpc[ k ], '\n' )


def checkMPCComet( data ):
    for i in range( 0, len( data ) ):
        line = " " + data[ i ] # Add extra ' ' to offset the zero column.
        message = ""
        if "****" in line: # https://github.com/skyfielders/python-skyfield/issues/503#issuecomment-745277162
            message += "Asterisks present\n"

        if len( line[ 92 : 95 + 1 ].strip() ) == 0:
            message += "Missing absolute magnitude\n"

        if len( line[ 97 : 100 + 1 ].strip() ) == 0:
            message += "Missing slope parameter\n"

        if message:
            print( message, line )


def checkMPCMinorPlanet( data ):
    for i in range( 0, len( data ) ):
        line = " " + data[ i ] # Add extra ' ' to offset the zero column.
        message = ""
        if "****" in line: # https://github.com/skyfielders/python-skyfield/issues/503#issuecomment-745277162
            message += "Asterisks present\n"

        if len( line[ 9 : 13 + 1 ].strip() ) == 0:
            message += "Missing absolute magnitude\n"

        if len( line[ 15 : 19 + 1 ].strip() ) == 0:
            message += "Missing slope parameter\n"

        if len( line[ 93 : 103 + 1 ].strip() ) == 0: # https://github.com/skyfielders/python-skyfield/issues/449#issuecomment-694159517
            message += "Missing semi-major axis\n"

        if message:
            print( message, line )


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


def getUnpackedDate( packedDate ):
    values = [ 'OFFSET ', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V' ]
    packedDatePadded = " " + packedDate # Add extra space for zero offset.

    year = str( values.index( packedDatePadded[ 1 ] ) ) + packedDatePadded[ 2 : 4 ]

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


#  # ['', '506074 2015 UM67', 'e', '6.0025', '150.1033', '132.1864', '1.558187', '0.5067277', '0.68704842', '10.0259', '09/04.0/2017', '2000', 'H18.9', '0.15\n'] 
#  #  o6074   18.9   0.15 K1794  10.02591  132.18641  150.10332    6.00251  0.6870484  0.50672775   1.5581871  1 MPO420174   266   3 2015-2017 0.31 M-v 3Eh MPC        0000         (506074)
# 09/04/2017

# Ephem minor planet format: http://www.clearskyinstitute.com/xephem/help/xephem.html#mozTocId215848
# MPC minor planet format: https://www.minorplanetcenter.net/iau/info/MPOrbitFormat.html
def compareMinorPlanets( minorPlanetsMPC, minorPlanetsXephem ):
    xephem = { }
    for i in range( 0, len( minorPlanetsXephem ) ):
        if not minorPlanetsXephem[ i ].startswith( "#" ):
            firstCommaIndex = minorPlanetsXephem[ i ].find( ',' )
            name = minorPlanetsXephem[ i ][ 0 : firstCommaIndex ]
            designation = getDesignationMinorPlanet(name )
            if designation == -1:
                print( "Unknown/bad designation:\n", minorPlanetsXephem[ i ] )

            else:
                xephem[ designation ] = ',' + minorPlanetsXephem[ i ] # Add extra ',' to offset the zero column.

    mpc = { }
    for i in range( 0, len( minorPlanetsMPC ) ):
        name = minorPlanetsMPC[ i ][ 166 : 194 ].strip() # Indices are offset by 1.
        designation = getDesignationMinorPlanet( name )
        if designation == -1:
            print( "Unknown/bad designation:\n", minorPlanetsMPC[ i ] )

        else:
            mpc[ designation ] = ' ' + minorPlanetsMPC[ i ] # Add ' ' to align column index with list index.

    missing = [ k for k in xephem.keys() if k not in mpc ]
    if missing:    
        print( "Minor planets in XEphem not in MPC:", missing )

    missing = [ k for k in mpc.keys() if k not in xephem ]
    if missing:
        print( "Minor planets in MPC not in XEphem:", missing )    

    for k in xephem.keys():
        if k in mpc:
            xephemData = xephem[ k ].split( ',' )
            message = ""
            # if float( xephemData[ 3 ] ) != float( mpc[ k ][ 60 : 68 + 1 ] ):
            #     message += "Mismatch of inclination\n"
            #
            # if float( xephemData[ 4 ] ) != float( mpc[ k ][ 49 : 57 + 1 ] ):
            #     message += "Mismatch of longitude of ascending node\n"
            #
            # if float( xephemData[ 5 ] ) != float( mpc[ k ][ 38 : 46 + 1 ] ):
            #     message += "Mismatch of argument of perihelion\n"

            if not math.isclose( float( xephemData[ 6 ] ), float( mpc[ k ][ 93 : 103 + 1 ] ), abs_tol = 1e-03 ):
                message += "Mismatch of semi-major axis (mean distance)\n"

            # if not math.isclose( float( xephemData[ 7 ] ), float( mpc[ k ][ 81 : 91 + 1 ] ), abs_tol = 1e-06 ):
            #     message += "Mismatch of mean daily motion\n"
            #
            # if float( xephemData[ 8 ][ 1 : ] ) != float( mpc[ k ][ 71 : 79 + 1 ] ):
            #     message += "Mismatch of eccentricity\n"
            #
            # if float( xephemData[ 9 ] ) != float( mpc[ k ][ 27 : 35 + 1 ] ):
            #     message += "Mismatch of mean anomoly\n"
            #
            # if xephemData[ 10 ] != getUnpackedDate( mpc[ k ][ 21 : 25 + 1 ] ):
            #     message += "Mismatch of epoch date\n"
            #
            # if len( xephemData[ 12 ] ) > 2 and float( xephemData[ 12 ][ 1 : ] ) != float( mpc[ k ][ 9 : 13 + 1 ] ): # Skip of absolute magnitude missing number component.
            #     message += "Mismatch of absolute magnitude\n"
            #
            # if len( mpc[ k ][ 15 : 19 + 1 ].strip() ) > 0 and float( xephemData[ 13 ] ) != float( mpc[ k ][ 15 : 19 + 1 ] ):
            #     message += "Mismatch of slope parameter\n"

            if message:
                print( message, xephemData, '\n', mpc[ k ], '\n' )


cometsMPC = getData( COMET_URL_MPC )
# checkMPCComet( cometsMPC )
cometsXephem = getData( COMET_URL_XEPHEM )
# checkXephem( cometsXephem )
# compareComets( cometsMPC, cometsXephem )                                            # Lots of epoch date mismatches!

minorPlanetsBrightMPC = getData( MINOR_PLANET_BRIGHT_URL_MPC )
# checkMPCMinorPlanet( minorPlanetsBrightMPC )
minorPlanetsBrightXephem = getData( MINOR_PLANET_BRIGHT_URL_XEPHEM )
# checkXephem( minorPlanetsBrightXephem )
# compareMinorPlanets( minorPlanetsBrightMPC, minorPlanetsBrightXephem )              # Lots of mismatches!

minorPlanetsCriticalMPC = getData( MINOR_PLANET_CRITICAL_URL_MPC )
# checkMPCMinorPlanet( minorPlanetsCriticalMPC )
minorPlanetsCriticalXephem = getData( MINOR_PLANET_CRITICAL_URL_XEPHEM )
# checkXephem( minorPlanetsCriticalXephem )
# compareMinorPlanets( minorPlanetsCriticalMPC, minorPlanetsCriticalXephem )            # Lots of mismatches!

minorPlanetsDistantMPC = getData( MINOR_PLANET_DISTANT_URL_MPC )
# checkMPCMinorPlanet( minorPlanetsDistantMPC )                                        # Missing absolute magnitude and slope parameter.
minorPlanetsDistantXephem = getData( MINOR_PLANET_DISTANT_URL_XEPHEM )
# checkXephem( minorPlanetsDistantXephem )                                              # Missing absolute magnitude and slope parameter.
compareMinorPlanets( minorPlanetsDistantMPC, minorPlanetsDistantXephem )            # Lots of mismatches!

minorPlanetsUnusualMPC = getData( MINOR_PLANET_UNUSUAL_URL )
# checkMPCMinorPlanet( minorPlanetsUnusualMPC )                                        # Missing absolute magnitude and slope parameter.
minorPlanetsUnusualXephem = getData( MINOR_PLANET_UNUSUAL_URL_XEPHEM_FORMAT )
# checkXephem( minorPlanetsUnusualXephem )                                             # Missing absolute magnitude and slope parameter.
# compareMinorPlanets( minorPlanetsUnusualMPC, minorPlanetsUnusualXephem )            # Lots of mismatches!

# minorPlanetsDatabaseMPC = getData( "file:///home/bernard/Programming/Subversion/IndicatorLunar/src/MPCORB_WITHOUT_HEADER.DAT" )
# checkMPCMinorPlanet( minorPlanetsDatabaseMPC )