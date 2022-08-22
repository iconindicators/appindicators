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


# Download from URL, load from file and hold in memory
# apparent magnitude for comets and minor planets.


from abc import ABC, abstractmethod
from dataprovider import DataProvider

import datetime, requests


class DataProviderApparentMagnitude( DataProvider ):

    # Download apparent magnitude data for comets and minor planets and save to the given filename.
    @staticmethod
    def download( filename, logging, isComet, apparentMagnitudeMaximum = None ):
        logging.getLogger( "urllib3" ).propagate = False
        downloaded = False
        if isComet:
            pass # Nothing to do as comet data from COBS contains updated/corrected absolute magnitude data in the ephemerides.

        else:
            downloaded = DataProviderApparentMagnitude.__downloadFromLowellMinorPlanetServices( filename, logging, apparentMagnitudeMaximum )

        return downloaded


    # Downloads apparent magnitude data for minor planets from Lowell Minor Planet Services and saves to the given filename.
    def __downloadFromLowellMinorPlanetServices( filename, logging, apparentMagnitudeMaximum ):
        try:
            variables = { "date": datetime.date.today().isoformat(), "apparentMagnitude": apparentMagnitudeMaximum }

            query = """
                query AsteroidsToday( $date: date!, $apparentMagnitude: float8! )
                {
                    minorplanet
                    (
                        where:
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
                    )
                    {
                        ast_number
                        designameByIdDesignationPrimary { str_designame }
                        ephemeris
                        (
                            where:
                            {
                                _and: { eph_date: { _eq: $date } }
                            }
                        )
                        {
                          v_mag
                        }
                    }
                }
                """

            url = "https://astorbdb.lowell.edu/v1/graphql"
            json = { "query": query, "variables": variables }
            response = requests.post( url, None, json )
            data = response.json()
            minorPlanets = data[ "data" ][ "minorplanet" ]

            with open( filename, 'w' ) as f:
                for minorPlanet in minorPlanets:
                    primaryDesignation = minorPlanet[ "designameByIdDesignationPrimary" ][ "str_designame" ].strip()
                    apparentMagnitude = str( minorPlanet[ "ephemeris" ][ 0 ][ "v_mag" ] )
                    f.write( primaryDesignation + ',' + apparentMagnitude  + '\n' )

            downloaded = True

        except Exception as e:
            downloaded = False
            logging.error( "Error retrieving apparent magnitude data from " + str( url ) )
            logging.exception( e )

        return downloaded


    # Load apparent magnitude data from the given filename.
    #
    # Returns a dictionary:
    #    Key: Object/body name
    #    Value: AM object
    #
    # Otherwise, returns an empty dictionary and may write to the log.
    @staticmethod
    def load( filename, logging ):
        amData = { }
        try:
            with open( filename, 'r' ) as f:
                for line in f.read().splitlines():
                    lastComma = line.rfind( ',' )
                    name = line[ 0 : lastComma ]
                    apparentMagnitude = line[ lastComma + 1 : ]
                    am = AM( name, apparentMagnitude )
                    amData[ am.getName().upper() ] = am

        except Exception as e:
            amData = { }
            logging.exception( e )
            logging.error( "Error reading apparent magnitude data from: " + filename )

        return amData


# Hold apparent magnitude for comets and minor planets.
class AM( object ):

    def __init__( self, name, apparentMagnitude ):
        self.name = name
        self.apparentMagnitude = apparentMagnitude


    def getName( self ): return self.name


    def getApparentMagnitude( self ): return self.apparentMagnitude


    def __str__( self ): return self.name + ',' + self.apparentMagnitude


    def __repr__( self ): return self.__str__()


    def __eq__( self, other ): 
        return \
            self.__class__ == other.__class__ and \
            self.getName() == other.getName() and \
            self.getApparentMagnitude() == other.getApparentMagnitude()