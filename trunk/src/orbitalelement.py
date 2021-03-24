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


# Orbital Element - holds parameters to compute orbits for comets, minor planets, near earth objects, et al.


from enum import Enum
from urllib.request import urlopen

import indicatorbase, re


class OE( object ):

    class DataType( Enum ):
        SKYFIELD_COMET = 0
        SKYFIELD_MINOR_PLANET = 1
        XEPHEM_COMET = 2
        XEPHEM_MINOR_PLANET = 3


    def __init__( self, name, data, dataType ):
        self.name = name
        self.data = data
        self.dataType = dataType


    def getName( self ): return self.name


    def getData( self ): return self.data


    def getDataType( self ): return self.dataType


    def __str__( self ): return self.data


    def __repr__( self ): return self.__str__()


# Download OE data.
#
# Returns a dictionary:
#    Key: object name (upper cased)
#    Value: OE object
#
# Otherwise, returns an empty dictionary and may write to the log.
def download( url, dataType, logging = None ):
    oeData = { }
    try:
        data = urlopen( url, timeout = indicatorbase.IndicatorBase.URL_TIMEOUT_IN_SECONDS ).read().decode( "utf8" ).splitlines()

        if dataType == OE.DataType.SKYFIELD_COMET or dataType == OE.DataType.SKYFIELD_MINOR_PLANET:
            if dataType == OE.DataType.SKYFIELD_COMET:
                # Format: https://minorplanetcenter.net/iau/info/CometOrbitFormat.html
                start = 102
                end = 158

                # Drop data if magnitude is missing.
                firstMagnitudeFieldStart = 91
                firstMagnitudeFieldEnd = 95

                secondMagnitudeFieldStart = 96
                secondMagnitudeFieldEnd = 100

            else:
                # Format: https://minorplanetcenter.net/iau/info/MPOrbitFormat.html
                start = 166
                end = 194

                # Drop data if magnitude is missing.
                firstMagnitudeFieldStart = 8
                firstMagnitudeFieldEnd = 13

                secondMagnitudeFieldStart = 14
                secondMagnitudeFieldEnd = 19

                # Drop data when semi-major-axis is missing.
                # https://github.com/skyfielders/python-skyfield/issues/449#issuecomment-694159517
                semiMajorAxisFieldStart = 92
                semiMajorAxisFieldEnd = 103

            for i in range( 0, len( data ) ):
                if "****" in data[ i ]: # https://github.com/skyfielders/python-skyfield/issues/503#issuecomment-745277162
                    continue

                if data[ i ][ firstMagnitudeFieldStart : firstMagnitudeFieldEnd + 1 ].isspace():
                    continue

                if data[ i ][ secondMagnitudeFieldStart : secondMagnitudeFieldEnd + 1 ].isspace():
                    continue

                if dataType == OE.DataType.SKYFIELD_MINOR_PLANET and data[ i ][ semiMajorAxisFieldStart : semiMajorAxisFieldEnd + 1 ].isspace():
                    continue

                name = data[ i ][ start : end ].strip()
                oe = OE( name, data[ i ], dataType )
                oeData[ oe.getName().upper() ] = oe

        elif dataType == OE.DataType.XEPHEM_COMET or dataType == OE.DataType.XEPHEM_MINOR_PLANET:
            # Format: http://www.clearskyinstitute.com/xephem/help/xephem.html#mozTocId215848
            for i in range( 0, len( data ) ):

                # Drop comment lines.
                if data[ i ].startswith( "#" ):
                    continue

                # Drop lines with missing magnitude component.  #TODO Add lots more comments about this!
                firstComma = data[ i ].index( "," )
                secondComma = data[ i ].index( ",", firstComma + 1 )
                field2 = data[ i ][ firstComma + 1 : secondComma ]
                if field2 == 'e':
                    lastComma = data[ i ].rindex( "," )
                    secondLastComma = data[ i ][ : lastComma ].rindex( "," )
                    fieldSecondToLast = data[ i ][ secondLastComma + 1 : lastComma ]
                    if len( fieldSecondToLast ) == 1 and fieldSecondToLast.isalpha():
                        continue

                # Remove spurious "****".
                # https://github.com/skyfielders/python-skyfield/issues/503#issuecomment-745277162
                if "****" in data[ i ]:
                    continue

                name = re.sub( "\s\s+", "", data[ i ][ 0 : data[ i ].index( "," ) ] ) # The name can have multiple whitespace, so remove.


# # Field 2 = e => field 12 = g or H, field 13 = k or G, specified by a leading g or H in field 12 (no g or H implies H). 
# pyephemComet = "413P/Larson,e,15.9772,39.0258,186.0334,3.711010,0.1378687,0.42336952,343.5677,03/23.0/2021,2000,g 14.0,4.0" 
# _Hg, _Gk = testPyEphem( pyephemComet, utcNow, latitude, longitude, elevation )
# print( _Hg, _Gk )
# 
# # Field 2 = h => field 10 = g, field 11 = k
# pyephemComet = "C/2015 D3 (PANSTARRS),h,05/02.3218/2016,128.5493,157.0632,2.9458,1.003528,8.142955,2000,5.5,4.0"
# _g, _k = testPyEphem( pyephemComet, utcNow, latitude, longitude, elevation )
# print( _g, _k )
# 
# # Field 2 = p => field 9 = g, field 10 = k
# pyephemComet = "C/2018 F3 (Johnson),p,08/15.2314/2017,105.5348,293.0113,2.483172,173.0311,2000,13.0,4.0"
# _g, _k = testPyEphem( pyephemComet, utcNow, latitude, longitude, elevation )
# print( _g, _k )
# 
# # Field 2 = e => field 12 = g or H, field 13 = k or G, specified by a leading g or H in field 12 (no g or H implies H). 
# pyephemMinorPlanet = "2010 LG61,e,123.8859,317.3744,352.1688,7.366687,0.0492942,0.81371070,163.4277,04/27.0/2019,2000,H,0.15"
# _Hg, _Gk = testPyEphem( pyephemMinorPlanet, utcNow, latitude, longitude, elevation )
# print( _Hg, _Gk )  # INCORRECT: There is no value defined in the data for H.

                oe = OE( name, data[ i ], dataType )
                oeData[ oe.getName().upper() ] = oe

        if not oeData and logging:
            logging.error( "No OE data found at " + str( url ) )

    except Exception as e:
        oeData = { }
        if logging:
            logging.error( "Error retrieving OE data from " + str( url ) )
            logging.exception( e )

    return oeData

# download( "file:///home/bernard/Desktop/Soft00Cmt.txt", OE.DataType.SKYFIELD_COMET, None )
# download( "file:///home/bernard/Desktop/Soft00Bright.txt", OE.DataType.SKYFIELD_MINOR_PLANET, None )
# download( "file:///home/bernard/Desktop/Soft00CritList.txt", OE.DataType.SKYFIELD_MINOR_PLANET, None )
# download( "file:///home/bernard/Desktop/Soft00Distant.txt", OE.DataType.SKYFIELD_MINOR_PLANET, None )
# download( "file:///home/bernard/Desktop/Soft00Unusual.txt", OE.DataType.SKYFIELD_MINOR_PLANET, None )
# 
# download( "file:///home/bernard/Desktop/Soft03Cmt.txt", OE.DataType.XEPHEM_COMET, None )
# download( "file:///home/bernard/Desktop/Soft03Bright.txt", OE.DataType.XEPHEM_MINOR_PLANET, None )
# download( "file:///home/bernard/Desktop/Soft03CritList.txt", OE.DataType.XEPHEM_MINOR_PLANET, None )
# download( "file:///home/bernard/Desktop/Soft03Distant.txt", OE.DataType.XEPHEM_MINOR_PLANET, None )
# download( "file:///home/bernard/Desktop/Soft03Unusual.txt", OE.DataType.XEPHEM_MINOR_PLANET, None )