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


# Download from URL, load from file and hold in memory,
# orbital elements for comets and minor planets.


import datetime
from enum import Enum
import requests

from dataprovider import DataProvider
from indicatorbase import IndicatorBase


class DataProviderOrbitalElement( DataProvider ):

    # Download orbital element data and save to the given filename.
    @staticmethod
    def download( filename, logging, orbitalElementDataType, apparentMagnitudeMaximum ):
        logging.getLogger( "urllib3" ).propagate = False

        if orbitalElementDataType == OE.DataType.SKYFIELD_MINOR_PLANET or \
           orbitalElementDataType == OE.DataType.XEPHEM_MINOR_PLANET:
            downloaded = DataProviderOrbitalElement.__downloadFromLowellMinorPlanetServices(
                filename, logging, orbitalElementDataType, apparentMagnitudeMaximum )

        elif orbitalElementDataType == OE.DataType.SKYFIELD_COMET or \
             orbitalElementDataType == OE.DataType.XEPHEM_COMET:
            downloaded = DataProviderOrbitalElement.__downloadFromCometObservationDatabase(
                filename, logging, orbitalElementDataType )

        else:
            logging.error( "Unknown data type: " + str( orbitalElementDataType ) )
            downloaded = False

        return downloaded


    # Download orbital element data for minor planets from Lowell Minor Planet Services
    # and save to the given filename.
    @staticmethod
    def __downloadFromLowellMinorPlanetServices( filename, logging, orbitalElementDataType, apparentMagnitudeMaximum ):
        try:
            variables = { "date": datetime.date.today().isoformat(), "apparentMagnitude": apparentMagnitudeMaximum }

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
                            designameByIdDesignationName { str_designame }
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

            with open( filename, 'w' ) as f:
                for minorPlanet in minorPlanets:
                    asteroid_number = minorPlanet[ "minorplanet" ][ "ast_number" ]
                    if asteroid_number is None:
                        continue # Not all asteroids / minor planets have a number. 
                        #TODO Need to see what happens when a minor planet has no ast_number; maybe set the magnitude limit to 1000?

                    if minorPlanet[ "minorplanet" ][ "designameByIdDesignationName" ] is None:
                        continue # Not all asteroids / minor planets have names.

                    designationName = minorPlanet[ "minorplanet" ][ "designameByIdDesignationName" ][ "str_designame" ]

                    designation = str( asteroid_number ) + ' ' + designationName

                    absoluteMagnitude = str( minorPlanet[ "minorplanet" ][ 'h' ] )
                    slopeParameter = "0.15" # Slope parameter (hard coded as typically does not vary that much and will not be used to calculate apparent magnitude)
                    meanAnomalyEpoch = str( minorPlanet[ 'm' ] )
                    argumentPerihelion = str( minorPlanet[ "peri" ] )
                    longitudeAscendingNode = str( minorPlanet[ "node" ] )
                    inclinationToEcliptic = str( minorPlanet[ 'i' ] )
                    orbitalEccentricity = str( minorPlanet[ 'e' ] )
                    semimajorAxis = str( minorPlanet[ 'a' ] )

                    # XEphem has three formats for minor planets
                    # based on the value of the eccentricity ( < 1, == 1, > 1 ):
                    #   https://xephem.github.io/XEphem/Site/help/xephem.html#mozTocId468501
                    # When the eccentricity is >= 1, the format is the same and requires date of epoch of perihelion,
                    # which does not appear to be present in the Lowell data.
                    # After checking both the Minor Planet Center's MPCORB.DAT and Lowell's astorb.dat,
                    # there are no bodies for which the eccentricity is >= 1.0
                    # Therefore this should not be a problem of concern...
                    # ...however, screen out a body with such an eccentricity just to be safe!
                    if float( orbitalEccentricity ) >= 1.0:
                        logging.error( "Found a body with eccentricity >= 1.0:" )
                        logging.error( "\t" + str( minorPlanet ) )
                        continue

                    if orbitalElementDataType == OE.DataType.XEPHEM_MINOR_PLANET:
                        components = [
                            designation,
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

                        f.write( ','.join( components )  + '\n' )

                    else: # OE.DataType.SKYFIELD_MINOR_PLANET
                        components = [
                            ' ' * 7, # number or designation packed
                            ' ', # 8
                            str( round( float( absoluteMagnitude ), 2 ) ).rjust( 5 ),
                            ' ', # 14
                            str( round( float( slopeParameter ), 2 ) ).rjust( 5 ),
                            ' ', # 20
                            DataProviderOrbitalElement.getPackedDate( minorPlanet[ "epoch" ][ 0 : 4 ], minorPlanet[ "epoch" ][ 5 : 7 ], minorPlanet[ "epoch" ][ 8 : 10 ] ).rjust( 5 ),
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
                            designation.ljust( 194 - 167 + 1 ),
                            ' ' * 8 ] # date last observation

                        f.write( ''.join( components )  + '\n' )

            downloaded = True

        except Exception as e:
            downloaded = False
            logging.error( "Error retrieving orbital element data from " + str( url ) )
            logging.exception( e )

        return downloaded


    # https://www.minorplanetcenter.net/iau/info/PackedDates.html
    @staticmethod
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


    # Download orbital element data for comets from Comet Observation Database
    # and save to the given filename.
    @staticmethod
    def __downloadFromCometObservationDatabase( filename, logging, orbitalElementDataType ):
        url = "https://cobs.si/api/elements.api?mag=obs&is-active=true&is-observed=true"
        if orbitalElementDataType == OE.DataType.SKYFIELD_COMET:
            url += "&format=mpc"

        else: # Assume to be OE.DataType.PYEPHEM_COMET
            url += "&format=ephem"

        return IndicatorBase.download( url, filename, logging )


    # Load orbital element data from the given filename.
    #
    # Returns a dictionary:
    #    Key: Object/body name
    #    Value: OE object
    #
    # Otherwise, returns an empty dictionary and may write to the log.
    @staticmethod
    def load( filename, logging, orbitalElementDataType ):
        oeData = { }
        if orbitalElementDataType == OE.DataType.SKYFIELD_COMET or orbitalElementDataType == OE.DataType.SKYFIELD_MINOR_PLANET:
            if orbitalElementDataType == OE.DataType.SKYFIELD_COMET: # https://minorplanetcenter.net/iau/info/CometOrbitFormat.html
                nameStart = 103 - 1
                nameEnd = 158 - 1

            elif orbitalElementDataType == OE.DataType.SKYFIELD_MINOR_PLANET: # https://minorplanetcenter.net/iau/info/MPOrbitFormat.html
                nameStart = 167 - 1
                nameEnd = 194 - 1

            try:
                with open( filename, 'r' ) as f:
                    for line in f.read().splitlines():
                        name = line[ nameStart : nameEnd + 1 ].strip()
                        oe = OE( name, line, orbitalElementDataType )
                        oeData[ oe.getName().upper() ] = oe

            except Exception as e:
                oeData = { }
                logging.exception( e )
                logging.error( "Error reading orbital element data from: " + filename )

        elif orbitalElementDataType == OE.DataType.XEPHEM_COMET or orbitalElementDataType == OE.DataType.XEPHEM_MINOR_PLANET:
            try:
                with open( filename, 'r' ) as f:
                    for line in f.read().splitlines():
                        name = line[ : line.find( ',' ) ].strip()
                        oe = OE( name, line, orbitalElementDataType )
                        oeData[ oe.getName().upper() ] = oe

            except Exception as e:
                oeData = { }
                logging.exception( e )
                logging.error( "Error reading orbital element data from: " + filename )

        else:
            oeData = { }
            logging.error( "Unknown data type encountered when loading orbital elements from file: '" + str( orbitalElementDataType ) + "', '" + filename + "'" )

        return oeData


# Hold orbital element for a comet or minor planet.
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


    def getName( self ):
        return self.name


    def getData( self ):
        return self.data


    def getDataType( self ):
        return self.dataType


    def __str__( self ):
        return self.data


    def __repr__( self ):
        return self.__str__()


    def __eq__( self, other ):
        return \
            self.__class__ == other.__class__ and \
            self.getName() == other.getName() and \
            self.getData() == other.getData() and \
            self.getDataType() == other.getDataType()
