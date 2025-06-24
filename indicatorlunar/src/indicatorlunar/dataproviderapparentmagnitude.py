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


'''
Download from URL, load from file and hold in memory, apparent magnitude for
comets and minor planets.
'''


import datetime

import requests  #TODO Does this need to be installed via pip?  Can't "from urllib.request import urlopen" be used?

from requests.exceptions import RequestException  #TODO Does this need to be installed via pip?  Can't "from urllib.request import urlopen" be used?

from .dataprovider import DataProvider


class DataProviderApparentMagnitude( DataProvider ):
    '''
    Download and persist apparent magnitude for comets and minor planets.
    '''

    @staticmethod
    def download(
        filename,
        logging,
        is_comet,
        apparent_magnitude_maximum ):
        '''
        Download apparent magnitude data for comets and minor planets and save
        to the given filename.
        '''
        if is_comet:
            # COBS does not provide apparent magnitude data.
            # Instead, when downloading orbital element data,
            # a maximum apparent magnitude is used to filter.
            downloaded = False

        else:
            downloaded = (
                DataProviderApparentMagnitude._download_from_lowell(
                    filename, logging, apparent_magnitude_maximum ) )

        return downloaded


    @staticmethod
    def _download_from_lowell(
        filename,
        logging,
        apparent_magnitude_maximum ):
        '''
        Download apparent magnitude data for minor planets from Lowell Minor
        Planet Services and saves to the given filename.
        '''
        variables = {
            "date": datetime.date.today().isoformat(),
            "apparentMagnitude": apparent_magnitude_maximum }

        query = '''
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
                    designameByIdDesignationName { str_designame }
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
            '''

        url = "https://astorbdb.lowell.edu/v1/graphql"
        json = { "query": query, "variables": variables }
        try:
            response = requests.post( url, None, json, timeout = 5 )
            data = response.json()
            minor_planets = data[ "data" ][ "minorplanet" ]

            with open( filename, 'w', encoding = "utf-8" ) as f:
                for minor_planet in minor_planets:
                    asteroid_number = minor_planet[ "ast_number" ]
                    if asteroid_number is None:
                        continue # Not all minor planets have a number.

                    if minor_planet[ "designameByIdDesignationName" ] is None:
                        continue # Not all minor planets have names.

                    designation_name = (
                        minor_planet[ "designameByIdDesignationName" ][ "str_designame" ] )

                    apparent_magnitude = (
                        str( minor_planet[ "ephemeris" ][ 0 ][ "v_mag" ] ) )

                    f.write(
                        str( asteroid_number ) +
                        ' ' +
                        designation_name +
                        ',' +
                        apparent_magnitude +
                        '\n' )

            downloaded = True

        except RequestException as e:
            downloaded = False
            logging.error(
                f"Error retrieving apparent magnitude data from { str( url ) }" )

            logging.exception( e )

        return downloaded


    @staticmethod
    def load(
        filename,
        logging ):
        '''
        Load apparent magnitude data from the given filename.

        Returns a dictionary
            Key: Object/body name
            Value: ApparentMagnitude object

        Otherwise, returns an empty dictionary and may write to the log.
        '''
        am_data = { }
        with open( filename, 'r', encoding = "utf-8" ) as f:
            for line in f.read().splitlines():
                last_comma = line.rfind( ',' )
                name = line[ 0 : last_comma ]
                apparent_magnitude = line[ last_comma + 1 : ]
                am = ApparentMagnitude( name, apparent_magnitude )
                am_data[ am.get_name().upper() ] = am

        return am_data


class ApparentMagnitude():
    ''' Apparent magnitude for a comet or minor planet. '''

    def __init__(
        self,
        name,
        apparent_magnitude ):

        self.name = name
        self.apparent_magnitude = apparent_magnitude


    def get_name( self ):
        return self.name


    def get_apparent_magnitude( self ):
        return self.apparent_magnitude


    def __str__( self ):
        return self.name + ',' + self.apparent_magnitude


    def __repr__( self ):
        return self.__str__()


    def __eq__( self, other ):
        return (
            self.__class__ == other.__class__ and
            self.get_name() == other.get_name() and
            self.get_apparent_magnitude() == other.get_apparent_magnitude() )
