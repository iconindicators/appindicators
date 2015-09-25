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
    def __init__( self, portName, month, day, hour, minute, levelInMetres, tideType, url ):
        self.portName = portName
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.levelInMetres = levelInMetres
        self.tideType = tideType
        self.url = url


    def getPortName( self ): return self.portName


    def getMonth( self ): return self.month


    def getDay( self ): return self.day


    def getHour( self ): return self.hour


    def getMinute( self ): return self.minute


    def getType( self ): return self.tideType


    def getLevelInMetres( self ): return self.levelInMetres


    def getURL( self ): return self.url


    def __str__( self ): return str( self.portName ) + " | " + str( self.month ) + " | " + str( self.day ) + " | " + str( self.hour ) + " | " + str( self.minute ) + " | " + str( self.levelInMetres ) + " | " + str( self.tideType )


    def __repr__( self ): return self.__str__()