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
            if float( fields[ "NORAD_CAT_ID" ] ) > float( "339999" ):
                # The current version of python-sgp4 (a wrapper for C++ sgp)
                # has an upper limit of 339,999 for the NORAD catalog number:
                #   https://github.com/brandon-rhodes/pyephem/discussions/243
                # Therefore drop any satellite until sgp4 can handle up to 999,999,999.
                logging.warning(
                    "Dropping satellite with NORAD catalog number",  
                    fields[ "NORAD_CAT_ID" ],
                    "as it exceeds the python-sgp4 upper limit of 339999." )

            else:
                gp = GP( fields )
                data[ gp.getNumber() ] = gp

        return data


# Hold general perturbation for a satellite.
class GP( object ):

    def __init__( self, xmlFieldsFromOMM ):
        self.satelliteRecord = Satrec()
        omm.initialize( self.satelliteRecord, xmlFieldsFromOMM )

        # Satellite record does not hold the name.
        self.name = xmlFieldsFromOMM[ "OBJECT_NAME" ]

        # The TLE format supports a NORAD catalog number up to five alpha-numeric characters,
        # whereas OMM supports a NORAD catalog number from 1 up to 999,999,999.
        # The SGP4 exporter will throw an exception when converting from OMM to TLE
        # with a NORAD catalog number longer than five characters:
        #   https://github.com/brandon-rhodes/python-sgp4/issues/97#issuecomment-1525482029
        # Therefore, if/when required to obtain the TLE from the OMM data,
        # set the NORAD catalog number to '0' which, although is an invalid value,
        # can be ignored as the TLE is only needed to compute the satellite trajectory.
        self.number = self.satelliteRecord.satnum_str
        if len( xmlFieldsFromOMM[ "NORAD_CAT_ID" ] ) > 5:
            self.satelliteRecord.satnum_str = "00000"

        # Initialise on demand.
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
        if self.tleLineOne is None:
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
