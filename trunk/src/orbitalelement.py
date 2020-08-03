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


# Orbital Element - holds parameters to compute orbits for comets, minor planets, near earth objects, et al.


from urllib.request import urlopen

import indicatorbase, re


class OE( object ):
    def __init__( self, data, name ):
        self.data = data
        self.name = name

#TODO Testing
#         self.name = re.sub( "\s\s+", "", self.data[ 0 : self.data.index( "," ) ] ) # The name can have multiple whitespace, so remove.  #TODO Put back.


    def getName( self ): return self.name


    def getData( self ): return self.data


    def __str__( self ): return self.data


    def __repr__( self ): return self.__str__()


# Downloads OE data for an object in XEphem format from the URL.
#
# Returns a dictionary:
#    Key: object name (upper cased)
#    Value: OE object
#
# Otherwise, returns an empty dictionary and may write to the log.
def download( url, logging = None ):
#TODO Formats...
# cometDataPyEphem = "88P/Howell,e,4.3838,56.6855,235.9158,3.105749,0.1800755,0.56433269,348.3628,07/24.0/2020,2000,g 11.0,6.0
# 
# Format: https://minorplanetcenter.net/iau/info/CometOrbitFormat.html
# cometDataSkyfield = "0088P         2020 09 26.6239  1.353073  0.564333  235.9158   56.6855    4.3838  20200724  11.0  6.0  88P/Howell                                               MPEC 2019-JE2
# 
# minorPlanetDataPyEphem = "1 Ceres,e,10.5935,80.3099,73.1153,2.767046,0.2141309,0.07553468,352.2305,03/23.0/2018,2000,H 3.34,0.12
# 
# Format: https://minorplanetcenter.net/iau/info/MPOrbitFormat.html
# minorPlanetDataSkyfield = "00001    3.34  0.12 K183N 352.23052   73.11528   80.30992   10.59351  0.0755347  0.21413094   2.7670463  0 MPO431490  6689 114 1801-2018 0.60 M-v 30h MPC        0000              (1) Ceres
    oeData = { }
    try:
        data = urlopen( url, timeout = indicatorbase.IndicatorBase.URL_TIMEOUT_IN_SECONDS ).read().decode( "utf8" ).splitlines()
        j = 0
        k = 0
        l = 0
        print( len( data) )
        for i in range( 0, len( data ) ):
            line = data[ i ]
            if not line.startswith( "#" ):
                if line.count( "," ) > 5: # PyEphem/XEphem format.
                    name = re.sub( "\s\s+", "", line[ 0 : line.index( "," ) ] ) # The name can have multiple whitespace, so remove.
                    j+=1

                else: # Assume Minor Planet Center format, used by Skyfield.
                    l = len( line )
                    if len( line ) < 194: # Comet
                        name = line[ 102 : 158 ]
                        k+=1

                    else: # Assume Minor Planet
                        name = line[ 166 : 194 ]
                        l+=1

                print( name )
# Comet    
#     ('designation', (102, 158)),
#     ('reference', (159, 168)),

# Minor Planet     
#     ('designation', (166, 194)),
#     ('last_observation_date', (194, 202)),

#                 oe = OE( data[ i ].strip() )
#                 oeData[ oe.getName().upper() ] = oe

        print( j, k, l )
        if not oeData and logging:
            logging.error( "No OE data found at " + str( url ) )

    except Exception as e:
        oeData = { }
        if logging:
            logging.error( "Error retrieving OE data from " + str( url ) )
            logging.exception( e )

    return oeData


# Downloads OE data for an object in XEphem format from the URL.
#
# Returns a dictionary:
#    Key: object name (upper cased)
#    Value: OE object
#
# Otherwise, returns an empty dictionary and may write to the log.
def downloadORIGINAL( url, logging = None ):
    oeData = { }
    try:
        data = urlopen( url, timeout = indicatorbase.IndicatorBase.URL_TIMEOUT_IN_SECONDS ).read().decode( "utf8" ).splitlines()
        for i in range( 0, len( data ) ):
            if not data[ i ].startswith( "#" ):
                oe = OE( data[ i ].strip() )
                oeData[ oe.getName().upper() ] = oe

        if not oeData and logging:
            logging.error( "No OE data found at " + str( url ) )

    except Exception as e:
        oeData = { }
        if logging:
            logging.error( "Error retrieving OE data from " + str( url ) )
            logging.exception( e )

    return oeData