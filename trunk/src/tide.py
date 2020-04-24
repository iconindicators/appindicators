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


import datetime


class Type: H, L = range( 2 )


class Reading( object ):
    # portID: ID of the port/location (string).
    # year, month, day: numerical date components for when the tide occurs (integer).
    # hour, minute: numerical time components for when the tide occurs (integer), or optionally both None.
    # timezone: String format +HHMM or -HHMM, only applicable when hour/minute are valid, otherwise None.
    # levelInMetres: the (positive or negative) level of the tide in metres (float).
    # tideType: the type of the tide.
    # url: The URL used to source the tide information.
    def __init__( self, portID, year, month, day, hour, minute, timezone, levelInMetres, tideType, url ):
        self.portID = portID
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.timezone = timezone
        self.levelInMetres = levelInMetres
        self.tideType = tideType
        self.url = url


    def getPortID( self ): return self.portID


    def getYear( self ): return self.year


    def getMonth( self ): return self.month


    def getDay( self ): return self.day


    def getHour( self ): return self.hour


    def getMinute( self ): return self.minute


    def getTimezone( self ): return self.timezone


    # Returns the tide.Type for this tide.
    def getType( self ): return self.tideType


    # Returns the level of this tide in metres as a float.
    def getLevelInMetres( self ): return self.levelInMetres


    def getURL( self ): return self.url


    # Returns the date/time or date if time is unavailable in the port local timezone.
    def getDateTime( self ):
        if self.hour is None and self.minute is None and self.timezone is None:
            return datetime.date( self.year, self.month, self.day )
        else:
            dateString = str( self.year ) + " " + \
                         str( self.month ) +  " " + \
                         str( self.day ) +  " " + \
                         str( self.hour ) + " " + \
                         str( self.minute ) + " " + \
                         str( self.timezone )

            return datetime.datetime.strptime( dateString, "%Y %m %d %H %M %z" )


    def __str__( self ):
        return self.portID + " | " + \
               str( self.year ) + "-" + str( self.month ) + "-" + str( self.day ) + "-" + str( self.hour ) + "-" + str( self.minute ) + "-" + str( self.timezone ) + " | " + \
               str( self.levelInMetres ) + " | " + \
               ( "H" if self.tideType == Type.H else "L" )


    def __repr__( self ): return self.__str__()