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
Download from URL, load from file and hold in memory,
orbital elements for comets and minor planets.
'''


import datetime

from enum import auto, IntEnum

import requests

# from .dataprovider import DataProvider
# from .indicatorbase import IndicatorBase
#TODO Revert
from dataprovider import DataProvider
from indicatorbase import IndicatorBase

class DataProviderOrbitalElement( DataProvider ):
    ''' Download and persist orbital elements for comets and minor planets. '''

    @staticmethod
    def download(
        filename,
        logging,
        orbital_element_data_type,
        apparent_magnitude_maximum ):
        ''' Download orbital element data and save to the given filename. '''

        is_comet = (
            orbital_element_data_type in {
                OrbitalElement.DataType.SKYFIELD_COMET,
                OrbitalElement.DataType.XEPHEM_COMET } )

        is_minor_planet = (
            orbital_element_data_type in {
                OrbitalElement.DataType.SKYFIELD_MINOR_PLANET,
                OrbitalElement.DataType.XEPHEM_MINOR_PLANET } )

        if is_comet:
            downloaded = (
                DataProviderOrbitalElement._download_from_comet_observation_database(
                    filename,
                    logging,
                    orbital_element_data_type,
                    apparent_magnitude_maximum ) )

        elif is_minor_planet:
            downloaded = (
                DataProviderOrbitalElement._download_from_lowell_minor_planet_services(
                    filename,
                    logging,
                    orbital_element_data_type,
                    apparent_magnitude_maximum ) )

        else:
            logging.error(
                "Unknown data type: " + str( orbital_element_data_type ) )

            downloaded = False

        return downloaded


    @staticmethod
    def _download_from_lowell_minor_planet_services(
        filename,
        logging,
        orbital_element_data_type,
        apparent_magnitude_maximum ):
        '''
        Download orbital element data for minor planets from Lowell Minor
        Planet Services and save to the given filename.
        '''

        try:
            variables = {
                "date": datetime.date.today().isoformat(),
                "apparentMagnitude": apparent_magnitude_maximum }

            query = '''
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
                '''

            url = "https://astorbdb.lowell.edu/v1/graphql"
            json = { "query": query, "variables": variables }
            response = requests.post( url, None, json, timeout = 5 )
            data = response.json()
            minor_planets = data[ "data" ][ "query_closest_orbelements" ]

            with open( filename, 'w', encoding = "utf-8" ) as f:
                for minor_planet in minor_planets:
                    asteroid_number = (
                        minor_planet[ "minorplanet" ][ "ast_number" ] )

                    if asteroid_number is None:
                        # Not all asteroids / minor planets have a number.
                        continue

                    if minor_planet[ "minorplanet" ][ "designameByIdDesignationName" ] is None:
                        # Not all asteroids / minor planets have a number.
                        continue

                    designation_name = (
                        minor_planet[ "minorplanet" ][ "designameByIdDesignationName" ][ "str_designame" ] )

                    designation = (
                        str( asteroid_number ) + ' ' + designation_name )

                    absolute_magnitude = (
                        str( minor_planet[ "minorplanet" ][ 'h' ] ) )

                    # The slope parameter is hard coded; typically does not vary
                    # that much and is not used to calculate apparent magnitude.
                    slope_parameter = "0.15"

                    mean_anomaly_epoch = str( minor_planet[ 'm' ] )
                    argument_perihelion = str( minor_planet[ "peri" ] )
                    longitude_ascending_node = str( minor_planet[ "node" ] )
                    inclination_to_ecliptic = str( minor_planet[ 'i' ] )
                    orbital_eccentricity = str( minor_planet[ 'e' ] )
                    semimajor_axis = str( minor_planet[ 'a' ] )

                    # XEphem has three formats for minor planets
                    # based on the value of the eccentricity ( < 1, == 1, > 1 ):
                    #   https://xephem.github.io/XEphem/Site/help/xephem.html#mozTocId468501
                    # When the eccentricity is >= 1, the format is the same and
                    # requires date of epoch of perihelion, which does not
                    # appear to be present in the Lowell data.
                    # After checking both the Minor Planet Center's MPCORB.DAT
                    # and Lowell's astorb.dat, there are no bodies for which the
                    # eccentricity is >= 1.0
                    # Therefore this should not be a problem of concern;
                    # however, filter out such bodies just to be safe!
                    if float( orbital_eccentricity ) >= 1.0:
                        logging.error(
                            "Found a body with eccentricity >= 1.0:" )

                        logging.error( "\t" + str( minor_planet ) )
                        continue

                    if orbital_element_data_type == OrbitalElement.DataType.XEPHEM_MINOR_PLANET:
                        components = [
                            designation,
                            'e',
                            inclination_to_ecliptic,
                            longitude_ascending_node,
                            argument_perihelion,
                            semimajor_axis,
                            '0',
                            orbital_eccentricity,
                            mean_anomaly_epoch,
                            minor_planet[ "epoch" ][ 5 : 7 ] + '/' + minor_planet[ "epoch" ][ 8 : 10 ] + '/' + minor_planet[ "epoch" ][ 0 : 4 ],
                            "2000.0",
                            absolute_magnitude,
                            slope_parameter ]

                        f.write( ','.join( components )  + '\n' )

                    else: # OrbitalElement.DataType.SKYFIELD_MINOR_PLANET
                        components = [
                            ' ' * 7, # number or designation packed
                            ' ', # 8
                            str( round( float( absolute_magnitude ), 2 ) ).rjust( 5 ),
                            ' ', # 14
                            str( round( float( slope_parameter ), 2 ) ).rjust( 5 ),
                            ' ', # 20
                            DataProviderOrbitalElement.get_packed_date( minor_planet[ "epoch" ][ 0 : 4 ], minor_planet[ "epoch" ][ 5 : 7 ], minor_planet[ "epoch" ][ 8 : 10 ] ).rjust( 5 ),
                            ' ', # 26
                            str( round( float( mean_anomaly_epoch ), 5 ) ).rjust( 9 ),
                            ' ' * 2, # 36, 37
                            str( round( float( argument_perihelion ), 5 ) ).rjust( 9 ),
                            ' ' * 2, # 47, 48
                            str( round( float( longitude_ascending_node ), 5 ) ).rjust( 9 ),
                            ' ' * 2, # 58, 59
                            str( round( float( inclination_to_ecliptic ), 5 ) ).rjust( 9 ),
                            ' ' * 2, # 69, 70
                            str( round( float( orbital_eccentricity ), 7 ) ).rjust( 9 ),
                            ' ', # 80
                            ' ' * 11, # mean daily motion
                            ' ', # 92
                            str( round( float( semimajor_axis ), 7 ) ).rjust( 11 ),
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


    @staticmethod
    def get_packed_date(
        year,
        month,
        day ):
        '''
        https://www.minorplanetcenter.net/iau/info/PackedDates.html
        '''

        def get_packed_day_month( day_or_month ):
            if int( day_or_month ) < 10:
                packed_day_month = str( int( day_or_month ) )

            else:
                packed_day_month = chr( int( day_or_month ) - 10 + ord( 'A' ) )

            return packed_day_month


        packed_year = year[ 2 : ]
        if int( year ) < 1900:
            packed_year = 'I' + packed_year

        elif int( year ) < 2000:
            packed_year = 'J' + packed_year

        else:
            packed_year = 'K' + packed_year

        packed_month = get_packed_day_month( month )
        packed_day = get_packed_day_month( day )

        return packed_year + packed_month + packed_day


    @staticmethod
    def _download_from_comet_observation_database(
        filename,
        logging,
        orbital_element_data_type,
        apparent_magnitude_maximum ):
        '''
        Download orbital element data for comets from Comet Observation
        Database and save to the given filename.
        '''

        url = "https://cobs.si/api/elements.api"
        url += "?mag=obs"
        url += "&is-active=true"
        url += "&is-observed=true"
        url += "&cur-mag=" + str( int( apparent_magnitude_maximum ) )

        if orbital_element_data_type == OrbitalElement.DataType.SKYFIELD_COMET:
            url += "&format=mpc"

        else: # Assume to be OrbitalElement.DataType.PYEPHEM_COMET
            url += "&format=ephem"

        return IndicatorBase.download( url, filename, logging )


    @staticmethod
    def load(
        filename,
        logging,
        orbital_element_data_type ):
        '''
        Load orbital element data from the given filename.

        Returns a dictionary:
            Key: Object/body name
            Value: OrbitalElement object

        Otherwise, returns an empty dictionary and may write to the log.
        '''
        oe_data = { }

        is_skyfield_data = (
            orbital_element_data_type in {
                OrbitalElement.DataType.SKYFIELD_COMET,
                OrbitalElement.DataType.SKYFIELD_MINOR_PLANET } )

        is_xephem_data = (
            orbital_element_data_type in {
                OrbitalElement.DataType.XEPHEM_COMET,
                OrbitalElement.DataType.XEPHEM_MINOR_PLANET } )

        if is_skyfield_data:
            if orbital_element_data_type == OrbitalElement.DataType.SKYFIELD_COMET:
                # https://minorplanetcenter.net/iau/info/CometOrbitFormat.html
                name_start = 103
                name_end = 158
                valid_indices = [ 13, 14, 19, 22, 30, 40, 41, 50, 51, 60, 61, 70, 71, 80, 81, 90, 91, 96, 101, 102, 159 ]

            else:
                # https://minorplanetcenter.net/iau/info/MPOrbitFormat.html
                name_start = 167
                name_end = 194
                valid_indices = [ 8, 14, 20, 26, 36, 37, 47, 48, 58, 59, 69, 70, 80, 92, 104, 105, 107, 117, 123, 127, 137, 142, 146, 150, 161, 166 ] # Ignore 132.

            with open( filename, 'r', encoding = "utf-8" ) as f:
                for line in f.read().splitlines():
                    keep = True
                    for i in valid_indices:
                        if len( line [ i - 1 ].strip() ) > 0:
                            keep = False
                            break

                    if keep:
                        name = line[ name_start - 1 : name_end - 1 + 1 ].strip()
                        oe = OrbitalElement( name, line, orbital_element_data_type )
                        oe_data[ oe.get_name().upper() ] = oe

        elif is_xephem_data:
            with open( filename, 'r', encoding = "utf-8" ) as f:
                for line in f.read().splitlines():
                    if not line.startswith( '{' ):
                        # Sometimes the COBS download emits an error message
                        # of the form:
                        #   {"code": "400",
                        #    "message": "Invalid integer value provided in the parameter.",
                        #    "moreInfo": "invalid literal for int() with base 10: 'false'",
                        #    "signature": {"source": "COBS Query API", "version": "1.3", "date": "2024 May"}}
                        # In this event, keep the download file as is for bug
                        # tracking if needed, but skip loading the data as there
                        # is no data to load.  When the cache becomes stale,
                        # a fresh and hopefully successful download will occur.
                        name = line[ : line.find( ',' ) ].strip()
                        oe = OrbitalElement( name, line, orbital_element_data_type )
                        oe_data[ oe.get_name().upper() ] = oe

        else:
            oe_data = { }
            message = (
                "Unknown data type encountered when loading orbital elements " +
                "from file: " +
                f"'{ str( orbital_element_data_type ) }', '{ filename }'" )

            logging.error( message )

        return oe_data


class OrbitalElement():
    ''' Orbital element for a comet or minor planet. '''

    class DataType( IntEnum ):
        ''' Data types for supported real objects. '''
        SKYFIELD_COMET = auto()
        SKYFIELD_MINOR_PLANET = auto()
        XEPHEM_COMET = auto()
        XEPHEM_MINOR_PLANET = auto()


    def __init__(
        self,
        name,
        data,
        data_type ):

        self.name = name
        self.data = data
        self.data_type = data_type


    def get_name( self ):
        return self.name


    def get_data( self ):
        return self.data


    def get_data_type( self ):
        return self.data_type


    def __str__( self ):
        return self.data


    def __repr__( self ):
        return self.__str__()


    def __eq__( self, other ):
        return (
            self.__class__ == other.__class__ and
            self.get_name() == other.get_name() and
            self.get_data() == other.get_data() and
            self.get_data_type() == other.get_data_type() )
