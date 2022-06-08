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


# Orbital Element - holds parameters to compute orbits for comets and minor planets.


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


    def __eq__( self, other ): 
        return \
            self.__class__ == other.__class__ and \
            self.getName() == other.getName() and \
            self.getData() == other.getData() and \
            self.getDataType() == other.getDataType()


# Download OE data; drop bad/missing data.
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
                # The format starts from 1, whereas the data is in a list/string which starts from 0, therefore, for all indices, subtract 1.
                nameStart = 103 - 1
                nameEnd = 158 - 1
                firstMagnitudeFieldStart = 92 - 1
                firstMagnitudeFieldEnd = 95 - 1
                secondMagnitudeFieldStart = 97 - 1
                secondMagnitudeFieldEnd = 100 - 1

            else:
                # Format: https://minorplanetcenter.net/iau/info/MPOrbitFormat.html
                nameStart = 167 - 1
                nameEnd = 194 - 1
                firstMagnitudeFieldStart = 9 - 1
                firstMagnitudeFieldEnd = 13 - 1
                secondMagnitudeFieldStart = 15 - 1
                secondMagnitudeFieldEnd = 19 - 1
                semiMajorAxisFieldStart = 93 - 1
                semiMajorAxisFieldEnd = 103 - 1

            for i in range( 0, len( data ) ):
                if "****" in data[ i ]: # https://github.com/skyfielders/python-skyfield/issues/503#issuecomment-745277162
                    continue

                # Missing absolute magnitude.
                if data[ i ][ firstMagnitudeFieldStart : firstMagnitudeFieldEnd + 1 ].isspace():
                    continue

                # Missing slope parameter.
                if data[ i ][ secondMagnitudeFieldStart : secondMagnitudeFieldEnd + 1 ].isspace():
                    continue

                # Missing semi-major-axis; https://github.com/skyfielders/python-skyfield/issues/449#issuecomment-694159517
                if dataType == OE.DataType.SKYFIELD_MINOR_PLANET and data[ i ][ semiMajorAxisFieldStart : semiMajorAxisFieldEnd + 1 ].isspace():
                    continue

                name = data[ i ][ nameStart : nameEnd + 1 ].strip()

                oe = OE( name, data[ i ], dataType )
                oeData[ oe.getName().upper() ] = oe

        else: # OE.DataType.XEPHEM_COMET or OE.DataType.XEPHEM_MINOR_PLANET
            # Format: http://www.clearskyinstitute.com/xephem/help/xephem.html#mozTocId215848
            for i in range( 0, len( data ) ):
                if data[ i ].startswith( "#" ): # Skip comment lines.
                    continue

                if "****" in data[ i ]: # https://github.com/skyfielders/python-skyfield/issues/503#issuecomment-745277162
                    continue

                # Drop lines with missing magnitude component.
                # There are three possible data formats depending on the second field value: either 'e', 'p' or 'h'.
                # Have noticed for format 'e' the magnitude component may be absent.
                # https://github.com/brandon-rhodes/pyephem/issues/196
                # Good data:
                #    2010 LO33,e,17.8383,241.0811,80.8229,23.10129,0.0088767,0.31984018,339.3447,04/27.0/2019,2000,H 8.5,0.15
                # Bad data:
                #    2010 LG61,e,123.8859,317.3744,352.1688,7.366687,0.0492942,0.81371070,163.4277,04/27.0/2019,2000,H,0.15
                firstComma = data[ i ].index( "," )
                secondComma = data[ i ].index( ",", firstComma + 1 )
                field2 = data[ i ][ firstComma + 1 : secondComma ]
                if field2 == 'e':
                    lastComma = data[ i ].rindex( "," )
                    secondLastComma = data[ i ][ : lastComma ].rindex( "," )
                    fieldSecondToLast = data[ i ][ secondLastComma + 1 : lastComma ]
                    if len( fieldSecondToLast ) == 1 and fieldSecondToLast.isalpha(): # Missing magnitude component.
                        continue

                name = re.sub( "\s\s+", "", data[ i ][ 0 : data[ i ].index( "," ) ] ) # The name can have multiple whitespace, so remove.

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


def downloadNEW( url, dataType, logging = None ):
    oeData = { }
    try:
        data = urlopen( url, timeout = indicatorbase.IndicatorBase.URL_TIMEOUT_IN_SECONDS ).read().decode( "utf8" ).splitlines()
        if dataType == OE.DataType.SKYFIELD_COMET or dataType == OE.DataType.SKYFIELD_MINOR_PLANET:
            if dataType == OE.DataType.SKYFIELD_COMET:
                # Format: https://minorplanetcenter.net/iau/info/CometOrbitFormat.html
                # The format starts from 1, whereas the data is in a list/string which starts from 0, therefore, for all indices, subtract 1.
                nameStart = 103 - 1
                nameEnd = 158 - 1
                firstMagnitudeFieldStart = 92 - 1
                firstMagnitudeFieldEnd = 95 - 1
                secondMagnitudeFieldStart = 97 - 1
                secondMagnitudeFieldEnd = 100 - 1

            else:
                # Format: https://minorplanetcenter.net/iau/info/MPOrbitFormat.html
                nameStart = 167 - 1
                nameEnd = 194 - 1
                firstMagnitudeFieldStart = 9 - 1
                firstMagnitudeFieldEnd = 13 - 1
                secondMagnitudeFieldStart = 15 - 1
                secondMagnitudeFieldEnd = 19 - 1
                semiMajorAxisFieldStart = 93 - 1
                semiMajorAxisFieldEnd = 103 - 1

            for i in range( 0, len( data ) ):
                if "****" in data[ i ]: # https://github.com/skyfielders/python-skyfield/issues/503#issuecomment-745277162
                    continue

                # Missing absolute magnitude.
                if data[ i ][ firstMagnitudeFieldStart : firstMagnitudeFieldEnd + 1 ].isspace():
                    continue

                # Missing slope parameter.
                if data[ i ][ secondMagnitudeFieldStart : secondMagnitudeFieldEnd + 1 ].isspace():
                    continue

                # Missing semi-major-axis; https://github.com/skyfielders/python-skyfield/issues/449#issuecomment-694159517
                if dataType == OE.DataType.SKYFIELD_MINOR_PLANET and data[ i ][ semiMajorAxisFieldStart : semiMajorAxisFieldEnd + 1 ].isspace():
                    continue

                name = data[ i ][ nameStart : nameEnd + 1 ].strip()

                oe = OE( name, data[ i ], dataType )
                oeData[ oe.getName().upper() ] = oe

        else: # OE.DataType.XEPHEM_COMET or OE.DataType.XEPHEM_MINOR_PLANET
            # Format: http://www.clearskyinstitute.com/xephem/help/xephem.html#mozTocId215848
            for i in range( 0, len( data ) ):
                if data[ i ].startswith( "#" ): # Skip comment lines.
                    continue

                if "****" in data[ i ]: # https://github.com/skyfielders/python-skyfield/issues/503#issuecomment-745277162
                    continue

                # Drop lines with missing magnitude component.
                # There are three possible data formats depending on the second field value: either 'e', 'p' or 'h'.
                # Have noticed for format 'e' the magnitude component may be absent.
                # https://github.com/brandon-rhodes/pyephem/issues/196
                # Good data:
                #    2010 LO33,e,17.8383,241.0811,80.8229,23.10129,0.0088767,0.31984018,339.3447,04/27.0/2019,2000,H 8.5,0.15
                # Bad data:
                #    2010 LG61,e,123.8859,317.3744,352.1688,7.366687,0.0492942,0.81371070,163.4277,04/27.0/2019,2000,H,0.15
                firstComma = data[ i ].index( "," )
                secondComma = data[ i ].index( ",", firstComma + 1 )
                field2 = data[ i ][ firstComma + 1 : secondComma ]
                if field2 == 'e':
                    lastComma = data[ i ].rindex( "," )
                    secondLastComma = data[ i ][ : lastComma ].rindex( "," )
                    fieldSecondToLast = data[ i ][ secondLastComma + 1 : lastComma ]
                    if len( fieldSecondToLast ) == 1 and fieldSecondToLast.isalpha(): # Missing magnitude component.
                        continue

                name = re.sub( "\s\s+", "", data[ i ][ 0 : data[ i ].index( "," ) ] ) # The name can have multiple whitespace, so remove.

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


def getName( line, dataType ):
    if dataType == OE.DataType.SKYFIELD_COMET or dataType == OE.DataType.SKYFIELD_MINOR_PLANET:
        if dataType == OE.DataType.SKYFIELD_COMET:
            # Format: https://minorplanetcenter.net/iau/info/CometOrbitFormat.html
            # The format starts from 1, whereas the data is in a list/string which starts from 0, therefore, for all indices, subtract 1.
            nameStart = 103 - 1
            nameEnd = 158 - 1

        else:
            # Format: https://minorplanetcenter.net/iau/info/MPOrbitFormat.html
            nameStart = 167 - 1
            nameEnd = 194 - 1

        name = line[ nameStart : nameEnd + 1 ].strip()

    else: # OE.DataType.XEPHEM_COMET or OE.DataType.XEPHEM_MINOR_PLANET
        # Format: http://www.clearskyinstitute.com/xephem/help/xephem.html#mozTocId215848
        name = re.sub( "\s\s+", "", line[ 0 : line.find( "," ) ] ) # The name can have multiple whitespace, so remove.

    return name