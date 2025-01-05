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


''' Encapsulates tidal readings. '''


class Reading():
    ''' Information for a single tidal event. '''

    def __init__( self, date, time, location, is_high, level, url ):
        '''
        date: Date of reading, as a string.
        time: Time of reading, as a string.
        location: Name of port or place.
        level: The tide level, as a string.
        is_high: True if the tide is high; false otherwise.
        url: The URL used to source the tide information.
        '''
        self.date = date
        self.time = time
        self.location = location
        self._is_high = is_high
        self.level = level
        self.url = url


    def get_date( self ):
        return self.date


    def get_time( self ):
        return self.time


    def get_location( self ):
        return self.location


    def is_high( self ):
        ''' Returns true if tide is high; false otherwise. '''
        return self._is_high


    def get_level( self ):
        ''' Returns the level of this tide. '''
        return self.level


    def get_url( self ):
        return self.url


    def __str__( self ):
        return (
            self.date + " | " +
            self.time + " | " +
            self.location + " | " +
            str( self._is_high ) + " | " +
            str( self.level ) + " | " +
            self.url )


    def __repr__( self ):
        return self.__str__()


    def __eq__( self, other ):
        return (
            self.__class__ == other.__class__ and
            self.get_date() == other.get_date() and
            self.get_time() == other.get_time() and
            self.get_location() == other.get_location() and
            self.is_high() == other.is_high() and
            self.get_level() == other.get_level() and
            self.get_url() == other.get_url() )
