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


# Two Line Element - holds parameters to compute orbit for satellites.
#
# https://www.celestrak.com/NORAD/documentation/tle-fmt.php
# https://en.wikipedia.org/wiki/Two-line_element_set


from urllib.request import urlopen


URL_TIMEOUT_IN_SECONDS = 20


class TLE( object ):
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
        launchYear = self._getLaunchYear()
        if int( launchYear ) < 57:
            launchYear = "20" + launchYear

        else:
            launchYear = "19" + launchYear

        return launchYear + "-" + self.line1[ 11 : 17 ].strip()


    def _getLaunchYear( self ): return self.line1[ 9 : 11 ]


    # Have found the launch year can be missing and subsequently throws an exception.
    # Screen out for missing/bad data in the launch year as a first attempt.
    def _isValid( self ):
        valid = True
        try:
            int( self._getLaunchYear() )
            valid = True

        except ValueError:
            valid = False

        return valid


    def __str__( self ):
        return \
            str( self.title ) + " | " + \
            str( self.line1 ) + " | " + \
            str( self.line2 )


    def __repr__( self ): return self.__str__()


    def __eq__( self, other ): 
        return \
            self.__class__ == other.__class__ and \
            self.getTitle() == other.getTitle() and \
            self.getLine1() == other.getLine1() and \
            self.getLine2() == other.getLine2()


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
        data = urlopen( url, timeout = URL_TIMEOUT_IN_SECONDS ).read().decode( "utf8" ).splitlines()
        for i in range( 0, len( data ), 3 ):
            tle = TLE( data[ i ].strip(), data[ i + 1 ].strip(), data[ i + 2 ].strip() )
            if tle._isValid():
                tleData[ ( tle.getNumber() ) ] = tle

            else:
                if logging:
                    logging.error( "Missing/bad launch year:" )
                    logging.error( "\t" + data[ i ] )
                    logging.error( "\t" + data[ i + 1 ] )
                    logging.error( "\t" + data[ i + 2 ] )

        if not tleData and logging:
            logging.error( "No TLE data found at " + str( url ) )

    except Exception as e:
        tleData = { }
        if logging:
            logging.error( "Error retrieving TLE data from " + str( url ) )
            logging.exception( e )

    return tleData


def toText( dictionary ):
    text = ""
    for tle in dictionary.values():
        text += tle.getTitle() + '\n' + tle.getLine1() + '\n' + tle.getLine2() + '\n'

    return text


def toDictionary( text ):
    tleData = { }
    i = 0
    splitText = text.splitlines()
    for i in range( 0, len( splitText ), 3 ):
        tle = TLE( splitText[ i ].strip(), splitText[ i + 1 ].strip(), splitText[ i + 2 ].strip() )
        tleData[ ( tle.getNumber() ) ] = tle

    return tleData