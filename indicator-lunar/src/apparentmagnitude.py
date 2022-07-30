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


# Apparent Magnitude - holds the apparent magnitude for comets and minor planets.


import datetime, requests


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


def download( isComet, apparentMagnitudeMaximum = None, logging = None ):
    logging.getLogger( "urllib3" ).propagate = False
    apparentMagnitudeData = { }
    if isComet:
        pass #TODO Waiting on COBS.

    else:
        apparentMagnitudeData = __downloadFromLowellMinorPlanetServices( apparentMagnitudeMaximum, logging )

    return apparentMagnitudeData


# Download AM data.
#
# Returns a dictionary:
#    Key: object name
#    Value: AM object
#
# Otherwise, returns an empty dictionary and may write to the log.
def __downloadFromLowellMinorPlanetServices( apparentMagnitudeMaximum, logging = None ):
    apparentMagnitudeData = { }
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

        for minorPlanet in minorPlanets:
            primaryDesignation = minorPlanet[ "designameByIdDesignationPrimary" ][ "str_designame" ].strip()
            apparentMagnitude = str( minorPlanet[ "ephemeris" ][ 0 ][ "v_mag" ] )

            am = AM( primaryDesignation, apparentMagnitude )
            apparentMagnitudeData[ am.getName().upper() ] = am

    except Exception as e:
        apparentMagnitudeData = { }
        if logging:
            logging.error( "Error retrieving apparent magnitude data from " + str( url ) )
            logging.exception( e )

    return apparentMagnitudeData


def toText( dictionary ):
    text = ""
    for am in dictionary.values():
        text += str( am ) + '\n'

    return text


def toDictionary( text ):
    amData = { }
    for line in text.splitlines():
        lastComma = line.rfind( ',' )
        name = line[ 0 : lastComma ]
        apparentMagnitude = line[ lastComma + 1 : ]
        am = AM( name, apparentMagnitude )
        amData[ am.getName().upper() ] = am

    return amData