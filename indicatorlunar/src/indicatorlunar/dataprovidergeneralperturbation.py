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
# general perturbations for satellites.


from sgp4 import alpha5, exporter, omm
from sgp4.api import Satrec

from dataprovider import DataProvider
from indicatorbase import IndicatorBase


class DataProviderGeneralPerturbation( DataProvider ):

    # Download general perturbation data from Celestrak
    # and save to the given filename.
    @staticmethod
    def download( filename, logging ):
        url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=visual&FORMAT=xml"
        return IndicatorBase.download( url, filename, logging )


    # Load general perturbation data from the given filename.
    #
    # Returns a dictionary:
    #    Key: Satellite catalog number (NORAD number)
    #    Value: GP object
    #
    # Otherwise, returns an empty dictionary and may write to the log.
    @staticmethod
    def load( filename, logging ):
        data = { }
        for fields in omm.parse_xml( filename ):
            gp = GP( fields )
            data[ gp.getNumber() ] = gp

        return data


class GP( object ):
    '''Hold general perturbation for a satellite.'''

    def __init__( self, xmlFieldsFromOMM ):
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
        is still available via getNumber().
        '''

        self.satelliteRecord = Satrec()

        # Satellite record does not hold the name.
        self.name = xmlFieldsFromOMM[ "OBJECT_NAME" ]

        self.number = xmlFieldsFromOMM[ "NORAD_CAT_ID" ]
        if float( xmlFieldsFromOMM[ "NORAD_CAT_ID" ] ) > float( "339999" ):
            xmlFieldsFromOMM[ "NORAD_CAT_ID" ] = '0'
            omm.initialize( self.satelliteRecord, xmlFieldsFromOMM ) # The satellite record now has a satnum = 0.
            xmlFieldsFromOMM[ "NORAD_CAT_ID" ] = self.number

        else:
            omm.initialize( self.satelliteRecord, xmlFieldsFromOMM )

        # Generate on demand.
        self.tleLineOne = None
        self.tleLineTwo = None


    def getName( self ):
        return self.name


    def getNumber( self ):
        return self.number


    def getInternationalDesignator( self ):
        return self.satelliteRecord.intldesg


    def getSatelliteRecord( self ):
        return self.satelliteRecord


    def getTLELineOneLineTwo( self ):
        '''
        The TLE format supports a NORAD catalog number of five characters,
        whereas OMM supports a NORAD catalog number from 1 up to 999,999,999.

        When generating the TLE, if the length of the NORAD catalog number
        exceeds five characters, the NORAD catalog number will be set to '0'
        in the TLE, which makes no impact upon computing satellite trajectory.

        The actual NORAD catalog number is still available via getNumber().
        '''
        if self.tleLineOne is None:
            if float( self.getNumber() ) > float( "339999" ):
                # The satnum was set to '0' in the init, so safe to do an export.
                self.tleLineOne, self.tleLineTwo = exporter.export_tle( self.satelliteRecord )

            elif len( self.getNumber() ) > 5:
                # https://github.com/brandon-rhodes/python-sgp4/issues/97#issuecomment-1525482029
                self.satelliteRecord.satnum_str = "00000"
                self.tleLineOne, self.tleLineTwo = exporter.export_tle( self.satelliteRecord )
                self.satelliteRecord.satnum_str = alpha5.to_alpha5( int( self.getNumber() ) )

            else:
                self.tleLineOne, self.tleLineTwo = exporter.export_tle( self.satelliteRecord )

        return self.tleLineOne, self.tleLineTwo


    def __str__( self ):
        return \
            self.name + " | " + \
            str( self.getNumber() ) + " | " + \
            self.getInternationalDesignator()


    def __repr__( self ):
        return self.__str__()


    def __eq__( self, other ):
        return \
            self.__class__ == other.__class__ and \
            self.getName() == other.getName() and \
            self.getSatelliteRecord() == other.getSatelliteRecord()
