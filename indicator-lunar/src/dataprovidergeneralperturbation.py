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
    # If instructed, will drop any satellite with a satellite number (Norad number)
    # greater than five digits, as this is incompatible with the TLE format.
    # https://github.com/brandon-rhodes/pyephem/discussions/243
    #
    # Returns a dictionary:
    #    Key: Satellite number (Norad number)
    #    Value: GP object
    #
    # Otherwise, returns an empty dictionary and may write to the log.
    @staticmethod
    def load( filename, logging, dropSatelliteNumberGreaterThanLengthFive ):
        data = { }
        for fields in omm.parse_xml( filename ):
            satelliteRecord = Satrec()
            omm.initialize( satelliteRecord, fields )
            if dropSatelliteNumberGreaterThanLengthFive and len( str( satelliteRecord.satnum ) ) > 5:
                continue

            data[ str( satelliteRecord.satnum ) ] = GP( fields[ "OBJECT_NAME" ], satelliteRecord ) 

        return data


# Hold general perturbations for satellites.
class GP( object ):
    def __init__( self, name, satelliteRecord ):
        self.name = name
        self.satelliteRecord = satelliteRecord


    def getInternationalDesignator( self ):  return self.satelliteRecord.intldesg


    def getLineOneLineTwo( self ): return exporter.export_tle( self.satelliteRecord )


    def getName( self ): return self.name


    def getNumber( self ): return str( self.satelliteRecord.satnum )
    
    
    def getSatelliteRecord( self ): return self.satelliteRecord


    def __str__( self ):
        return \
            self.name + " | " + \
            str( self.getNumber() ) + " | " + \
            self.getInternationalDesignator()


    def __repr__( self ): return self.__str__()


    def __eq__( self, other ): 
        return \
            self.__class__ == other.__class__ and \
            self.getName() == other.getName() and \
            self.getSatelliteRecord() == other.getSatelliteRecord()