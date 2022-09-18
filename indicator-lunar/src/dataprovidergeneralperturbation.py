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


# Download from URL, load from file and hold in memory general perturbations for satellites.


from dataprovider import DataProvider
from indicatorbase import IndicatorBase
from sgp4 import exporter, omm
from sgp4.api import Satrec


class DataProviderGeneralPerturbation( DataProvider ):

    # Download general perturbation data from Celestrak and save to the given filename.
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


# Hold general perturbation for a satellite.
class GP( object ):

    def __init__( self, xmlFieldsFromOMM ):
        self.name = xmlFieldsFromOMM[ "OBJECT_NAME" ]

        self.satelliteRecord = Satrec()
        omm.initialize( self.satelliteRecord, xmlFieldsFromOMM )

        # The TLE format does not support a satellite catalog number (NORAD number) greater than 99,999.
        # Therefore, when the satellite information is requested as a TLE,
        # substitute '0' for the satellite catalog number when in excess of 99,999.
        #
        # Unfortunately, cannot alter the satellite catalog number once it is set as it is protected.
        # Instead, keep a second record around as required.
        self.satelliteRecordTLESafe = self.satelliteRecord
        if int( xmlFieldsFromOMM[ "NORAD_CAT_ID" ] ) > 99999:
            self.satelliteRecordTLESafe = Satrec()
            xmlFieldsFromOMM[ "NORAD_CAT_ID" ] = str( 0 )
            omm.initialize( self.satelliteRecordTLESafe, xmlFieldsFromOMM )

        self.tleLineOne = None
        self.tleLineTwo = None


    def getInternationalDesignator( self ):
        return self.satelliteRecord.intldesg


    def getTLELineOneLineTwo( self ):
        if self.tleLineOne is None:
            self.tleLineOne, self.tleLineTwo = exporter.export_tle( self.satelliteRecordTLESafe )

        return self.tleLineOne, self.tleLineTwo


    def getName( self ):
        return self.name


    def getNumber( self ):
        return str( self.satelliteRecord.satnum )


    def getSatelliteRecord( self ):
        return self.satelliteRecord


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