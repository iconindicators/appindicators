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
general perturbations for satellites.
'''


from sgp4 import alpha5, exporter, omm
from sgp4.api import Satrec

from dataprovider import DataProvider
from indicatorbase import IndicatorBase


class DataProviderGeneralPerturbation( DataProvider ):
    ''' Download and persist general pertubation for satellites. '''

    @staticmethod
    def download(
        filename,
        logging ):
        '''
        Download general perturbation data from Celestrak and save to the
        given filename.
        '''
        url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=visual&FORMAT=xml"
        return IndicatorBase.download( url, filename, logging )


    @staticmethod
    def load(
        filename,
        logging ):
        '''
        Load general perturbation data from the given filename.

        Returns a dictionary:
            Key: Satellite catalog number (NORAD number)
            Value: GP object

        Otherwise, returns an empty dictionary and may write to the log.
        '''
        data = { }
        for fields in omm.parse_xml( filename ):
            gp = GP( fields )
            data[ gp.get_number() ] = gp

        return data


class GP():
    '''Hold general perturbation for a satellite.'''

    def __init__(
        self,
        xml_fields_from_omm ):
        '''
        Take the XML fields from the OMM data and propagate.

        Unfortunately, the underlying C++ sgp, which performs the propagation,
        has an upper limit of 339,999 for the NORAD catalog number:
            https://github.com/brandon-rhodes/pyephem/discussions/243

        Use a sleight of hand to ensure propagation occurs
        when the NORAD catalog number exceeds 339,999:
            Swap out the NORAD catalog number with '0'
            (NORAD catalog numbers start from '1'),
            perform the propagation, then swap back in.

        Although the resultant satellite record will contain a value of '0'
        for the NORAD catalog number, the actual NORAD catalog number
        is still available via get_number().
        '''

        self.satellite_record = Satrec()

        # Satellite record does not hold the name.
        self.name = xml_fields_from_omm[ "OBJECT_NAME" ]

        self.number = xml_fields_from_omm[ "NORAD_CAT_ID" ]
        if float( xml_fields_from_omm[ "NORAD_CAT_ID" ] ) > float( "339999" ):
            xml_fields_from_omm[ "NORAD_CAT_ID" ] = '0'

            # The satellite record now has a satnum = 0.
            omm.initialize( self.satellite_record, xml_fields_from_omm )

            xml_fields_from_omm[ "NORAD_CAT_ID" ] = self.number

        else:
            omm.initialize( self.satellite_record, xml_fields_from_omm )

        # Generate on demand.
        self.tle_line_one = None
        self.tle_line_two = None


    def get_name( self ):
        return self.name


    def get_number( self ):
        return self.number


    def get_international_designator( self ):
        return self.satellite_record.intldesg


    def get_satellite_record( self ):
        return self.satellite_record


    def get_tle_line_one_line_two( self ):
        '''
        The TLE format supports a NORAD catalog number of five characters,
        whereas OMM supports a NORAD catalog number from 1 up to 999,999,999.

        When generating the TLE, if the length of the NORAD catalog number
        exceeds five characters, the NORAD catalog number will be set to '0'
        in the TLE, which makes no impact upon computing satellite trajectory.

        The actual NORAD catalog number is still available via get_number().
        '''
        if self.tle_line_one is None:
            if float( self.get_number() ) > float( "339999" ):
                # The satnum was set to '0' in the init, so safe to do an export.
                self.tle_line_one, self.tle_line_two = (
                    exporter.export_tle( self.satellite_record ) )

            elif len( self.get_number() ) > 5:
                # https://github.com/brandon-rhodes/python-sgp4/issues/97#issuecomment-1525482029
                self.satellite_record.satnum_str = "00000"
                self.tle_line_one, self.tle_line_two = (
                    exporter.export_tle( self.satellite_record ) )
                self.satellite_record.satnum_str = (
                    alpha5.to_alpha5( int( self.get_number() ) ) )

            else:
                self.tle_line_one, self.tle_line_two = (
                    exporter.export_tle( self.satellite_record ) )

        return self.tle_line_one, self.tle_line_two


    def __str__( self ):
        return (
            self.name + " | " +
            str( self.get_number() ) + " | " +
            self.get_international_designator() )


    def __repr__( self ):
        return self.__str__()


    def __eq__( self, other ):
        return (
            self.__class__ == other.__class__ and
            self.get_name() == other.get_name() and
            self.get_satellite_record() == other.get_satellite_record() )
