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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# Two Line Element - holds parameters to compute orbit for satellites.


from urllib.request import urlopen

import indicatorbase


class TLE:
    def __init__( self, title, line1, line2 ):
        self.title = title
        self.line1 = line1
        self.line2 = line2


    def getTitle( self ): return self.title


    def getLine1( self ): return self.line1


    def getLine2( self ): return self.line2


    def getName( self ): return self.title


    def getNumber( self ): return self.line1[ 2 : 7 ]


    def getInternationalDesignator( self ): 
        launchYear = self.line1[ 9 : 11 ]
        if int( launchYear ) < 57:
            launchYear = "20" + launchYear
        else:
            launchYear = "19" + launchYear 

        return launchYear + "-" + self.line1[ 11 : 17 ].strip()


    def __str__( self ): return str( self.title ) + " | " + str( self.line1 ) + " | " + str( self.line2 )


    def __repr__( self ): return self.__str__()


# Downloads TLE data from the URL.
#
# Returns a dictionary:
#    Key: Satellite number
#    Value: TLE object
#
# Otherwise, returns an empty dictionary and may write to the log.
def download( url, logging = None ):
    tleData = { }
    try:
        data = urlopen( url, timeout = indicatorbase.IndicatorBase.URL_TIMEOUT_IN_SECONDS ).read().decode( "utf8" ).splitlines()
        for i in range( 0, len( data ), 3 ):
            tle = TLE( data[ i ].strip(), data[ i + 1 ].strip(), data[ i + 2 ].strip() )
            tleData[ ( tle.getNumber() ) ] = tle

        if not tleData and logging:
            logging.error( "No TLE data found at " + str( url ) )

    except Exception as e:
        tleData = { }
        if logging:
            logging.error( "Error retrieving TLE data from " + str( url ) )
            logging.exception( e )

    return tleData