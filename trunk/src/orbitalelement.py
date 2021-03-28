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
        print( url )
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

                # Drop data when semi-major-axis is missing (only applies to minor planets).
                # https://github.com/skyfielders/python-skyfield/issues/449#issuecomment-694159517
                semiMajorAxisFieldStart = 92
                semiMajorAxisFieldEnd = 103

            for i in range( 0, len( data ) ):
                if "****" in data[ i ]: # https://github.com/skyfielders/python-skyfield/issues/503#issuecomment-745277162
                    print( data[ i ][ start : end ].strip() )
                    continue

                if data[ i ][ firstMagnitudeFieldStart : firstMagnitudeFieldEnd + 1 ].isspace():
                    print( data[ i ][ start : end ].strip() )
                    continue

                if data[ i ][ secondMagnitudeFieldStart : secondMagnitudeFieldEnd + 1 ].isspace():
                    print( data[ i ][ start : end ].strip() )
                    continue

                if dataType == OE.DataType.SKYFIELD_MINOR_PLANET and data[ i ][ semiMajorAxisFieldStart : semiMajorAxisFieldEnd + 1 ].isspace():
                    print( data[ i ][ start : end ].strip() )
                    continue

                name = data[ i ][ start : end ].strip()

                oe = OE( name, data[ i ], dataType )
                oeData[ oe.getName().upper() ] = oe

        elif dataType == OE.DataType.XEPHEM_COMET or dataType == OE.DataType.XEPHEM_MINOR_PLANET:
            # Format: http://www.clearskyinstitute.com/xephem/help/xephem.html#mozTocId215848
            for i in range( 0, len( data ) ):

                # Skip comment lines.
                if data[ i ].startswith( "#" ):
                    continue

                # Drop lines with missing magnitude component.
                # There are three possible data formats depending on the second field value: either 'e', 'p' or 'h'.
                # Have noticed for format 'e' the magnitude component may be absent.
                # https://github.com/brandon-rhodes/pyephem/issues/196
                # Good data:
                #    413P/Larson,e,15.9772,39.0258,186.0334,3.711010,0.1378687,0.42336952,343.5677,03/23.0/2021,2000,g 14.0,4.0
                # Bad data:
                #    2010 LG61,e,123.8859,317.3744,352.1688,7.366687,0.0492942,0.81371070,163.4277,04/27.0/2019,2000,H,0.15
                firstComma = data[ i ].index( "," )
                secondComma = data[ i ].index( ",", firstComma + 1 )
                field2 = data[ i ][ firstComma + 1 : secondComma ]
                if field2 == 'e':
                    lastComma = data[ i ].rindex( "," )
                    secondLastComma = data[ i ][ : lastComma ].rindex( "," )
                    fieldSecondToLast = data[ i ][ secondLastComma + 1 : lastComma ]
                    if len( fieldSecondToLast ) == 1 and fieldSecondToLast.isalpha():
                        print( re.sub( "\s\s+", "", data[ i ][ 0 : data[ i ].index( "," ) ] ) )
                        continue

                # Drop if spurious "****" is present.
                # https://github.com/skyfielders/python-skyfield/issues/503#issuecomment-745277162
                if "****" in data[ i ]:
                    print( re.sub( "\s\s+", "", data[ i ][ 0 : data[ i ].index( "," ) ] ) )
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


download( "file:///home/bernard/Desktop/Soft03Cmt.txt", OE.DataType.XEPHEM_COMET, None )
download( "file:///home/bernard/Desktop/Soft03Bright.txt", OE.DataType.XEPHEM_MINOR_PLANET, None )
download( "file:///home/bernard/Desktop/Soft03CritList.txt", OE.DataType.XEPHEM_MINOR_PLANET, None )
download( "file:///home/bernard/Desktop/Soft03Distant.txt", OE.DataType.XEPHEM_MINOR_PLANET, None )
download( "file:///home/bernard/Desktop/Soft03Unusual.txt", OE.DataType.XEPHEM_MINOR_PLANET, None )

# download( "file:///home/bernard/Desktop/Soft00Cmt.txt", OE.DataType.XEPHEM_COMET, None )
# download( "file:///home/bernard/Desktop/Soft00Bright.txt", OE.DataType.SKYFIELD_MINOR_PLANET, None )
# download( "file:///home/bernard/Desktop/Soft00CritList.txt", OE.DataType.SKYFIELD_MINOR_PLANET, None )
# download( "file:///home/bernard/Desktop/Soft00Distant.txt", OE.DataType.SKYFIELD_MINOR_PLANET, None )
# download( "file:///home/bernard/Desktop/Soft00Unusual.txt", OE.DataType.SKYFIELD_MINOR_PLANET, None )


# K17M07B 14.2   0.15 K1794   0.00140   80.46498   58.25502   55.71379  0.9987471  0.00000466                MPO435133    33   1  174 days 0.34         MPC        0000         2017 MB7
# K10A85Z             K1014 177.05658  265.65797   63.71372   17.76664  0.0000826  0.56584942   1.4476674  E MPO221139     9   1    1 days 0.47         MPC        0000         2010 AZ85

# 
# 1 -   7    Number or provisional designation
# 9 -  13    Absolute magnitude, H
# 15 -  19   Slope parameter, G
# 21 -  25   Epoch (packed form)
# 27 -  35   Mean anomaly
# 38 -  46   Argument of perihelion
# 49 -  57   Longitude of the ascending node
# 60 -  68   Inclination to the ecliptic
# 71 -  79   Orbital eccentricity
# 81 -  91   Mean daily motion
# 93 - 103   Semimajor axis
# 106        Uncertainty parameter
# 108 - 116  Reference
# 118 - 122  Number of observations
# 124 - 126  Number of oppositions
# 128 - 131  Year of first observation
# 132        '-'
# 133 - 136  Year of last observation
# 138 - 141  r.m.s residual (")
# 143 - 145  Coarse indicator of perturbers
# 147 - 149  Precise indicator of perturbers
# 151 - 160  Computer name
# 162 - 165  4-hexdigit flags
# 167 - 194  Readable designation
# 195 - 202  Date of last observation included in
# 
# 
#    1     2    3       4       5     6       7        8         9         10          11   12    13
# 2017 MB7,e,55.7138,58.2550,80.4650,3549,0.0000047,0.99874708,0.0000,11/08.6577/2016,2000,H14.2,0.15
#
#     1     2    3       4        5         6        7         8        9        10        11   12  13
# 2010 AZ85,e,17.7666,63.7137,265.6580,1.447667,0.5658494,0.00008261,177.0566,01/04.0/2010,2000,H,0.15
#
# Field 1 One or more object names
# Field 2 Type designation, e the object type is elliptical heliocentric
# Field 3 i = inclination, degrees
# Field 4 O = longitude of ascending node, degrees
# Field 5 o = argument of perihelion, degrees
# Field 6 a = mean distance (aka semi-major axis), AU
# Field 7 n = mean daily motion, degrees per day (computed from a**3/2 if omitted)
# Field 8 e = eccentricity, must be < 1
# Field 9 M = mean anomaly, i.e., degrees from perihelion
# Field 10 E = epoch date, i.e., time of M
# Field 11 D = the equinox year, i.e., time of i, O and o
# Field 12 First component of magnitude model, either g from (g,k) or H from (H,G)
# Field 13 Second component of magnitude model, either k or G
# Field 14 s = angular size at 1 AU, arc seconds, optional


# Mean distance / Semi-major axis
# Field 6 = 3549
# 93 - 103 = <blank>

# Mean anomaly
# Field 9 = 0.0000
# 27 -  35 = 0.00140


# First component of magnitude model, either g from (g,k) or H from (H,G)
# Field 12 = <blank>
#  9 -  13 = <blank>

# Second component of magnitude model, either k or G
# Field 13 = 0.15
# 15 -  19 = <blank>


# Discrepancies between the MPC and XEphem format for Minor Planets
# 
# 
# I have noticed data in fields which don't correlate but assume should for the same body and attribute, irrespective of format.
# 
# 
# Example 1:  2017 MB7 found in  Soft00Distant.txt and Soft03Distant.txt
# 
# For the attribute of Mean distance / Semi-major axis, there are differences in values:
#     Field 6 = 3549 versus columns 93 - 103 = <blank>
# 
# For the attribute of Mean anomaly, again another difference:
#     Field 9 = 0.0000 versus columns 27 -  35 = 0.00140
# 
# 
# Example 2:  2010 AZ85 found in Soft00Unusual.txt and Soft03Unusual.txt
# 
# For the attribute of Second component of magnitude model, either k or G:
#     Field 13 = 0.15 versus columns 15 -  19 = <blank>
# 
# Could someone please look into this and let me know if I've made a mistake or if there is indeed a data error.
# 
# Thanks,
# 
# Bernard.
