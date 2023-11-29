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
            gp = GP( fields )
            data[ gp.getNumber() ] = gp

        return data


# Hold general perturbation for a satellite.
class GP( object ):

    def __init__( self, xmlFieldsFromOMM ):
        self.satelliteRecord = Satrec()
        omm.initialize( self.satelliteRecord, xmlFieldsFromOMM )

        self.name = xmlFieldsFromOMM[ "OBJECT_NAME" ] # Satellite record does not hold the name.

        # Initialise on demand.
        self.tleLineOne = None
        self.tleLineTwo = None


    def getName( self ):
        return self.name


    def getNumber( self ):
        return str( self.satelliteRecord.satnum )


    def getInternationalDesignator( self ):
        return self.satelliteRecord.intldesg


    def getSatelliteRecord( self ):
        return self.satelliteRecord


    def getTLELineOneLineTwo( self ):
        if self.tleLineOne is None:
            print( self.satelliteRecord.satnum_str )
            if self.satelliteRecord.satnum > 99999:
                print( self.satelliteRecord )
                # The TLE format does not support satellite catalog numbers (NORAD number) greater than 99,999.
                #
                # When the SGP4 exporter converts from OMM to TLE, such a catalog number will be erroneously omitted:
                #    https://github.com/brandon-rhodes/python-sgp4/issues/97
                #
                # Ideally set the catalog number to '0' (which is unused) after the OMM object is initialised
                # (before the export to TLE); unfortunately, the catalog number is protected.
                #
                # Therefore, export to OMM, set the catalog number to '0' then export to TLE.
#TODO Given the new writable field satnum_str in Satrec, the code below may be simplified.
# Not sure what to exactly write to the satnum_str field;
# currently setting a 0 to the NORAD_CAT_ID before converting to Satrec.
# So first need an example of a satnum > 99999 (in length, not value).
# Then set the satnum_str to the value from satelliteRecord.satnum
# and see what happens in the omm.initialise (does the value actually get set?)
# and after that, viewing the satellite info (name, number, rise, set, position)
# is all correct.
#   https://github.com/brandon-rhodes/python-sgp4/commit/19990f3f2a5af9d054a84797a8ede0892b487912
#   https://github.com/brandon-rhodes/python-sgp4/issues/97#issuecomment-1525482029
# Need to check in PyEphem as it likely won't support a satnum > 99999.  
# Need to check in Skyfield as it likely will support a satnum > 99999.
#
#
# Wondering now based on 
#   https://github.com/brandon-rhodes/pyephem/discussions/243
# seems SGP4 does not support numbers above a certain range,
# so dealing with a satnum > 99999 is somewhat of a false barrier...
# there is another barrier just waiting.
# So should I first confirm this?
# The suggestion is to swap out the satnum when too large for TLE
# at the time of passing in to be calculated...maybe that is an option.
# But if there is another barrier further along then what is the point?
# Need to investigate further...maybe ask Brandon in issue 243 above.
#
#
#Sent email to David dvallado@comspoc.com asking why if the noradID/satnum
# is supposed to be 9 digits, does that mean SGP4's satnum needs to change from 6 chars to 9?
#
# Also, based on
#   https://github.com/brandon-rhodes/python-sgp4/commit/56c1c4da0e9735b7a76939c2cb582bae134220ee,
# it seems that the upper limit of SGP4 (at least in python-sgp4) is satnum <= 339999.
                ommData = exporter.export_omm( self.satelliteRecord, self.getName() )
                ommData[ "NORAD_CAT_ID" ] = str( 0 )
                satelliteRecord = Satrec()
                omm.initialize( satelliteRecord, ommData )
                self.tleLineOne, self.tleLineTwo = exporter.export_tle( satelliteRecord )

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
