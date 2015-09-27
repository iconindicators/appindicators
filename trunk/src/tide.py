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


class Type: H, L = range( 2 )


class Reading:
    # portName: name of the port/location.
    # month, day, hour, minute: integer date/time components for when the tide type occurs.
    # levelInMetres: the level of the tide type (float, integer or string).
    # tideType: the type of the tide, either "H" or "L" string.
    # url: The URL used to source the tide information.
    def __init__( self, portName, month, day, hour, minute, levelInMetres, tideType, url ):
        self.portName = portName
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.levelInMetres = float( levelInMetres )
        self.url = url

        if tideType == "H":
            self.tideType = Type.H
        else:
            self.tideType = Type.L


    def getPortName( self ): return self.portName


    def getMonth( self ): return self.month


    def getDay( self ): return self.day


    def getHour( self ): return self.hour


    def getMinute( self ): return self.minute


    # Returns the tide.Type for this tide.
    def getType( self ): return self.tideType


    # Returns the level of this tide in metres as a float.
    def getLevelInMetres( self ): return self.levelInMetres


    def getURL( self ): return self.url


    def __str__( self ): return self.portName + " | " + str( self.month ) + "-" + str( self.day ) + "-" + str( self.hour ) + "-" + str( self.minute ) + " | " + str( self.levelInMetres ) + " | " + str( self.tideType )


    def __repr__( self ): return self.__str__()