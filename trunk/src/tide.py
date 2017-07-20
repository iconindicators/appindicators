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


import datetime


class Type: H, L = range( 2 )


class Reading:
    # portID: ID of the port/location (string).
    # year, month, day, hour, minute: numerical date/time components for when the tide type occurs (integer).
    # levelInMetres: the (positive or negative) level of the tide in metres (float).
    # tideType: the type of the tide.
    # url: The URL used to source the tide information.
    def __init__( self, portID, year, month, day, hour, minute, levelInMetres, tideType, url ):
        self.portID = portID
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.levelInMetres = levelInMetres
        self.tideType = tideType
        self.url = url


    def getPortID( self ): return self.portID


    def getYear( self ): return self.year


    def getMonth( self ): return self.month


    def getDay( self ): return self.day


    def getHour( self ): return self.hour


    def getMinute( self ): return self.minute


    # Returns the tide.Type for this tide.
    def getType( self ): return self.tideType


    # Returns the level of this tide in metres as a float.
    def getLevelInMetres( self ): return self.levelInMetres


    def getURL( self ): return self.url


    def getDateTimeUTC( self ):
        try: return datetime.datetime( self.year, self.month, self.day, self.hour, self.minute, 0, 0, datetime.timezone.utc )
        except TypeError: return datetime.date( self.year, self.month, self.day )


    def __str__( self ):
        return self.portID + " | " + \
                str( self.year ) + "-" + str( self.month ) + "-" + str( self.day ) + "-" + str( self.hour ) + "-" + str( self.minute ) + " | " + \
                str( self.levelInMetres ) + " | " + \
                ( "H" if self.tideType == Type.H else "L" )


    def __repr__( self ): return self.__str__()