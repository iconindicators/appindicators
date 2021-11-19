#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from enum import Enum
from urllib.request import urlopen

import indicatorbase, re


# class OE( object ):
#
#     class DataType( Enum ):
#         SKYFIELD_COMET = 0
#         SKYFIELD_MINOR_PLANET = 1
#         XEPHEM_COMET = 2
#         XEPHEM_MINOR_PLANET = 3
#
#
#     def __init__( self, name, data, dataType ):
#         self.name = name
#         self.data = data
#         self.dataType = dataType
#
#
#     def getName( self ): return self.name
#
#
#     def getData( self ): return self.data
#
#
#     def getDataType( self ): return self.dataType
#
#
#     def __str__( self ): return self.data
#
#
#     def __repr__( self ): return self.__str__()
#
#
#     def __eq__( self, other ): 
#         return \
#             self.__class__ == other.__class__ and \
#             self.getName() == other.getName() and \
#             self.getData() == other.getData() and \
#             self.getDataType() == other.getDataType()
#
#
# # Download OE data; drop bad/missing data.
# #
# # Returns a dictionary:
# #    Key: object name (upper cased)
# #    Value: OE object
# #
# # Otherwise, returns an empty dictionary and may write to the log.
# def download( url, dataType, logging = None ):
#     oeData = { }
#     try:
#         data = urlopen( url, timeout = indicatorbase.IndicatorBase.URL_TIMEOUT_IN_SECONDS ).read().decode( "utf8" ).splitlines()
#         if dataType == OE.DataType.SKYFIELD_COMET or dataType == OE.DataType.SKYFIELD_MINOR_PLANET:
#             if dataType == OE.DataType.SKYFIELD_COMET:
#                 # Format: https://minorplanetcenter.net/iau/info/CometOrbitFormat.html
#                 start = 102
#                 end = 158
#                 firstMagnitudeFieldStart = 91
#                 firstMagnitudeFieldEnd = 95
#                 secondMagnitudeFieldStart = 96
#                 secondMagnitudeFieldEnd = 100
#
#             else:
#                 # Format: https://minorplanetcenter.net/iau/info/MPOrbitFormat.html
#                 start = 166
#                 end = 194
#                 firstMagnitudeFieldStart = 8
#                 firstMagnitudeFieldEnd = 13
#                 secondMagnitudeFieldStart = 14
#                 secondMagnitudeFieldEnd = 19
#                 semiMajorAxisFieldStart = 92
#                 semiMajorAxisFieldEnd = 103
#
#             for i in range( 0, len( data ) ):
#                 if "****" in data[ i ]: # https://github.com/skyfielders/python-skyfield/issues/503#issuecomment-745277162
#                     continue
#
#                 # Missing absolute magnitude.
#                 if data[ i ][ firstMagnitudeFieldStart : firstMagnitudeFieldEnd + 1 ].isspace():
#                     continue
#
#                 # Missing slope parameter.
#                 if data[ i ][ secondMagnitudeFieldStart : secondMagnitudeFieldEnd + 1 ].isspace():
#                     continue
#
#                 # Missing semi-major-axis; https://github.com/skyfielders/python-skyfield/issues/449#issuecomment-694159517
#                 if dataType == OE.DataType.SKYFIELD_MINOR_PLANET and data[ i ][ semiMajorAxisFieldStart : semiMajorAxisFieldEnd + 1 ].isspace():
#                     continue
#
#                 name = data[ i ][ start : end ].strip()
#
#                 oe = OE( name, data[ i ], dataType )
#                 oeData[ oe.getName().upper() ] = oe
#
#         elif dataType == OE.DataType.XEPHEM_COMET or dataType == OE.DataType.XEPHEM_MINOR_PLANET:
#             # Format: http://www.clearskyinstitute.com/xephem/help/xephem.html#mozTocId215848
#             for i in range( 0, len( data ) ):
#                 if data[ i ].startswith( "#" ): # Skip comment lines.
#                     continue
#
#                 if "****" in data[ i ]: # https://github.com/skyfielders/python-skyfield/issues/503#issuecomment-745277162
#                     continue
#
#                 # Drop lines with missing magnitude component.
#                 # There are three possible data formats depending on the second field value: either 'e', 'p' or 'h'.
#                 # Have noticed for format 'e' the magnitude component may be absent.
#                 # https://github.com/brandon-rhodes/pyephem/issues/196
#                 # Good data:
#                 #    2010 LO33,e,17.8383,241.0811,80.8229,23.10129,0.0088767,0.31984018,339.3447,04/27.0/2019,2000,H 8.5,0.15
#                 # Bad data:
#                 #    2010 LG61,e,123.8859,317.3744,352.1688,7.366687,0.0492942,0.81371070,163.4277,04/27.0/2019,2000,H,0.15
#                 firstComma = data[ i ].index( "," )
#                 secondComma = data[ i ].index( ",", firstComma + 1 )
#                 field2 = data[ i ][ firstComma + 1 : secondComma ]
#                 if field2 == 'e':
#                     lastComma = data[ i ].rindex( "," )
#                     secondLastComma = data[ i ][ : lastComma ].rindex( "," )
#                     fieldSecondToLast = data[ i ][ secondLastComma + 1 : lastComma ]
#                     if len( fieldSecondToLast ) == 1 and fieldSecondToLast.isalpha(): # Missing magnitude component.
#                         continue
#
#                 name = re.sub( "\s\s+", "", data[ i ][ 0 : data[ i ].index( "," ) ] ) # The name can have multiple whitespace, so remove.
#
#                 oe = OE( name, data[ i ], dataType )
#                 oeData[ oe.getName().upper() ] = oe
#
#         if not oeData and logging:
#             logging.error( "No OE data found at " + str( url ) )
#
#     except Exception as e:
#         oeData = { }
#         if logging:
#             logging.error( "Error retrieving OE data from " + str( url ) )
#             logging.exception( e )
#
#     return oeData


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


def get( url ):
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

compareComets(
    get( COMET_URL_EPHEM_FORMAT ),
    get( COMET_URL_MPC_FORMAT ) )