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

import datetime, re, requests


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


def download( dataType, apparentMagnitudeMaximum = None, logging = None ):
    logging.getLogger( "urllib3" ).propagate = False
    oeData = { }
    if dataType == OE.DataType.SKYFIELD_MINOR_PLANET or dataType == OE.DataType.XEPHEM_MINOR_PLANET:
        oeData = __downloadFromLowellMinorPlanetServices( dataType, apparentMagnitudeMaximum, logging )

    if dataType == OE.DataType.SKYFIELD_COMET or dataType == OE.DataType.XEPHEM_COMET:
        pass #TODO Get data from COBS

    else:
        pass #TODO Log error or something?

    return oeData


#TODO Update header comment
# Download OE data; drop bad/missing data.
#
# Returns a dictionary:
#    Key: object name
#    Value: OE object
#
# Otherwise, returns an empty dictionary and may write to the log.
def __downloadFromLowellMinorPlanetServices( dataType, apparentMagnitudeMaximum, logging = None ):
    orbitalElementData = { }
    try:
        variables = { "date": datetime.date.today().isoformat(), "apparentMagnitude": apparentMagnitudeMaximum } #TODO Check if today or utctoday...ask Brian.

        query = """
            query AsteroidsToday( $date: date!, $apparentMagnitude: float8! )
            {
                query_closest_orbelements
                (
                    args: { query_date: $date },
                    where:
                    {
                        minorplanet:
                        {
                            ephemeris:
                            {
                                _and:
                                {
                                    eph_date: { _eq: $date },
                                    v_mag: { _lte: $apparentMagnitude }
                                }
                            }
                        }
                    }
                )
                {
                    minorplanet
                    {
                        ast_number
                        designameByIdDesignationPrimary { str_designame }
                        h # Absolute magnitude
                        ephemeris( where: { eph_date: { _eq: $date } } ) { v_mag }
                    }    
                    epoch # Epoch date
                    m # Mean anomaly epoch
                    peri # Argument of perhilion
                    node # Longitude of ascending node
                    i # Inclination to ecliptic
                    e # Orbital eccentricity
                    a # Semi-major axis
                }
            }
            """

        url = "https://astorbdb.lowell.edu/v1/graphql"
        json = { "query": query, "variables": variables }
        response = requests.post( url, None, json )
        data = response.json()
        minorPlanets = data[ "data" ][ "query_closest_orbelements" ]

        for minorPlanet in minorPlanets:
            number = str( minorPlanet[ "minorplanet" ][ "ast_number" ] or '' ).strip() # The asteroid number CAN be empty so need to avoid a None result.
            primaryDesignation = minorPlanet[ "minorplanet" ][ "designameByIdDesignationPrimary" ][ "str_designame" ].strip()
            id = ( number + ' ' + primaryDesignation ).strip()

            absoluteMagnitude = str( minorPlanet[ "minorplanet" ][ 'h' ] )
            slopeParameter = "0.15" # Slope parameter (hard coded as typically does not vary that much and will not be used to calculate apparent magnitude)
            epochDate = minorPlanet[ "epoch" ][ 5 : 7 ] + '/' + minorPlanet[ "epoch" ][ 8 : 10 ] + '/' + minorPlanet[ "epoch" ][ 0 : 4 ]
            meanAnomalyEpoch = str( minorPlanet[ 'm' ] )
            argumentPerihelion = str( minorPlanet[ "peri" ] )
            longitudeAscendingNode = str( minorPlanet[ "node" ] )
            inclinationToEcliptic = str( minorPlanet[ 'i' ] )
            orbitalEccentricity = str( minorPlanet[ 'e' ] )
            semimajorAxis = str( minorPlanet[ 'a' ] )

            if dataType == OE.DataType.XEPHEM_MINOR_PLANET:
                components = [
                    id,
                    'e',
                    inclinationToEcliptic,
                    longitudeAscendingNode,
                    argumentPerihelion,
                    semimajorAxis,
                    '0',
                    orbitalEccentricity,
                    meanAnomalyEpoch,
                    minorPlanet[ "epoch" ][ 5 : 7 ] + '/' + minorPlanet[ "epoch" ][ 8 : 10 ] + '/' + minorPlanet[ "epoch" ][ 0 : 4 ],
                    "2000.0",
                    absoluteMagnitude,
                    slopeParameter ]

                oe = OE( id, ','.join( components ), dataType )
                orbitalElementData[ oe.getName() ] = oe

            else: #OE.DataType.SKYFIELD_MINOR_PLANET
                components = [
                    ' ' * 7, # number or designation packed
                    ' ', # 8
                    str( round( float( absoluteMagnitude ), 2 ) ).rjust( 5 ),
                    ' ', # 14
                    str( round( float( slopeParameter ), 2 ) ).rjust( 5 ),
                    ' ', # 20
                    getPackedDate( minorPlanet[ "epoch" ][ 0 : 4 ], minorPlanet[ "epoch" ][ 5 : 7 ], minorPlanet[ "epoch" ][ 8 : 10 ] ).rjust( 5 ),
                    ' ', # 26
                    str( round( float( meanAnomalyEpoch ), 5 ) ).rjust( 9 ),
                    ' ' * 2, # 36, 37 
                    str( round( float( argumentPerihelion ), 5 ) ).rjust( 9 ),
                    ' ' * 2, # 47, 48
                    str( round( float( longitudeAscendingNode ), 5 ) ).rjust( 9 ),
                    ' ' * 2, # 58, 59
                    str( round( float( inclinationToEcliptic ), 5 ) ).rjust( 9 ),
                    ' ' * 2, # 69, 70
                    str( round( float( orbitalEccentricity ), 7 ) ).rjust( 9 ),
                    ' ', # 80
                    ' ' * 11, # mean daily motion
                    ' ', # 92
                    str( round( float( semimajorAxis ), 7 ) ).rjust( 11 ),
                    ' ' * 2, # 104, 105
                    ' ', # uncertainty parameter
                    ' ', # 107
                    ' ' * 9, # reference
                    ' ', # 117
                    ' ' * 5, # observations
                    ' ', # 123
                    ' ' * 3, # oppositions
                    ' ', # 127
                    ' ' * ( 4 + 1 + 4 ), # multiple/single oppositions
                    ' ', # 137
                    ' ' * 4, # rms residual
                    ' ', # 142
                    ' ' * 3, # coarse indicator of perturbers
                    ' ', # 146
                    ' ' * 3, # precise indicator of perturbers
                    ' ', # 150
                    ' ' * 10, # computer name
                    ' ', # 161
                    ' ' * 4, # hexdigit flags
                    ' ', # 166
                    id.ljust( 194 - 167 + 1 ),
                    ' ' * 8 ] # date last observation

                oe = OE( id, ''.join( components ), dataType )
                orbitalElementData[ oe.getName() ] = oe

    except Exception as e:
        orbitalElementData = { }
        if logging:
            logging.error( "Error retrieving orbital element data from " + str( url ) )
            logging.exception( e )

    return orbitalElementData


# https://www.minorplanetcenter.net/iau/info/PackedDates.html
def getPackedDate( year, month, day ):
    packedYear = year[ 2 : ]
    if int( year ) < 1900:
        packedYear = 'I' + packedYear

    elif int( year ) < 2000:
        packedYear = 'J' + packedYear

    else:
        packedYear = 'K' + packedYear


    def getPackedDayMonth( dayOrMonth ):
        if int( dayOrMonth ) < 10:
            packedDayMonth = str( int( dayOrMonth ) )

        else:
            packedDayMonth = chr( int( dayOrMonth ) - 10 + ord( 'A' ) )

        return packedDayMonth

    packedMonth = getPackedDayMonth( month )
    packedDay = getPackedDayMonth( day )

    return packedYear + packedMonth + packedDay


# Need a comment explaining why this is no longer in use.
# Download OE data; drop bad/missing data.
#
# Returns a dictionary:
#    Key: object name
#    Value: OE object
#
# Otherwise, returns an empty dictionary and may write to the log.
def __downloadFromMinorPlanetCenter( url, dataType, logging = None ):
    oeData = { }
    try:
        data = urlopen( url, timeout = 20 ).read().decode( "utf8" ).splitlines() # TODO If AstroBase will be used for something else, then add the timeout back here.
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
                oeData[ oe.getName() ] = oe

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
                oeData[ oe.getName() ] = oe

        if not oeData and logging:
            logging.error( "No orbital element data found at " + str( url ) )

    except Exception as e:
        oeData = { }
        if logging:
            logging.error( "Error retrieving orbital element data from " + str( url ) )
            logging.exception( e )

    return oeData


# TODO Is this valid now...I don't think so.  Is it even needed?
# I think it is used in the Preferences...figure out what is going on.
def getName( line, dataType ):
    print( "getName in orbitalelement")
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


def toText( dictionary ):
    text = ""
    for oe in dictionary.values():
        text += oe.getData() + '\n'

    return text


def toDictionary( text, dataType ):
    oeData = { }
    if dataType == OE.DataType.SKYFIELD_COMET or dataType == OE.DataType.SKYFIELD_MINOR_PLANET:
        if dataType == OE.DataType.SKYFIELD_COMET: # Format: https://minorplanetcenter.net/iau/info/CometOrbitFormat.html
            nameStart = 103 - 1
            nameEnd = 158 - 1
    
        elif dataType == OE.DataType.SKYFIELD_MINOR_PLANET: # Format: https://minorplanetcenter.net/iau/info/MPOrbitFormat.html
            nameStart = 167 - 1
            nameEnd = 194 - 1

        for line in text.splitlines():
            name = line[ nameStart : nameEnd + 1 ].strip()
            oe = OE( name, line, dataType )
            oeData[ oe.getName() ] = oe

    elif dataType == OE.DataType.XEPHEM_COMET or dataType == OE.DataType.XEPHEM_MINOR_PLANET:
        for line in text.splitlines():
            name = line[ : line.find( ',' ) ].strip()
            oe = OE( name, line, dataType )
            oeData[ oe.getName() ] = oe

    else:
        pass # TODO Barf or ignore?

    return oeData