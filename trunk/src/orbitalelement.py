#!/usr/bin/env python3


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


# Orbital Element - holds parameters to compute orbits for comets, minor planets, near earth objects, et al.


from urllib.request import urlopen

import re


class OE:
    def __init__( self, data ):
        self.data = data
        self.name = re.sub( "\s\s+", "", self.data[ 0 : self.data.index( "," ) ] ) # The name can have multiple whitespace, so remove.


    def getName( self ): return self.name


    def getData( self ): return self.data


    def __str__( self ): return self.data


    def __repr__( self ): return self.__str__()


# Downloads OE data in XEphem format from the URL.
#
# On success, returns a dict:
#    Key: comet name (upper cased)
#    Value: comet data line
#
# On error, may write to the log (if not None) and returns None.
def download( url, logging = None ):
    oeData = { }
    try:
        data = urlopen( url ).read().decode( "utf8" ).splitlines()
        for i in range( 0, len( data ) ):
            if not data[ i ].startswith( "#" ):
                oe = OE( data[ i ].strip() )
                oeData[ oe.getName().upper() ] = oe

    except Exception as e:
        oeData = None
        if logging is not None:
            logging.exception( e )
            logging.error( "Error retrieving OE data from " + str( url ) )

    return oeData