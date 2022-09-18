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
# general perturbations for satellites.


from abc import ABC, abstractmethod
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
        # names = { }
        # numbers = { }
        data = { }
        for fields in omm.parse_xml( filename ):
            satelliteRecord = Satrec()
            omm.initialize( satelliteRecord, fields )
            data[ str( satelliteRecord.satnum ) ] = GP( fields[ "OBJECT_NAME" ], satelliteRecord )

        return data


# Hold general perturbations for satellites.
class GP( object ):
    def __init__( self, name, satelliteRecord, satelliteRecordWithSatelliteNumberSetToZero = None ):
        self.name = name
        self.satelliteRecord = satelliteRecord
        self.satelliteRecordWithSatelliteNumberSetToZero = satelliteRecordWithSatelliteNumberSetToZero


    def getInternationalDesignator( self ):
        return self.satelliteRecord.intldesg


#TODO I think here the satellite record should be modified BEFORE passed to the exporter
# to change the satellite number to say 00000 if the satellite number is longer than five digits.
# FIRST check if 00000 is already taken.
    def getLineOneLineTwo( self ):
        lineOneLineTwo = None
        if self.satelliteRecord.satnum > 99999:
            print( "Swapping", self.satelliteRecord.satnum )
            satNum = self.satelliteRecord.satnum
            self.satelliteRecord.satnum = 0
            lineOneLineTwo = exporter.export_tle( self.satelliteRecord )
            self.satelliteRecord.satnum = satNum

        else:
            lineOneLineTwo = exporter.export_tle( self.satelliteRecord )

        return lineOneLineTwo


    def getName( self ):
        return self.name


    def getNumber( self ):
        return str( self.satelliteRecord.satnum )


    def getSatelliteRecord( self ):
        return self.satelliteRecord


#TODO NOt sure if this should be exposed.
    # def satelliteRecordWithSatelliteNumberSetToZero( self ):
    #     return self.satelliteRecordWithSatelliteNumberSetToZero


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