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


''' An event comprises a date and description. '''


class Event():
    ''' A single calendar event. '''

    def __init__(
        self,
        date,
        description ):
        '''
        Date
            String format 'MMM DD'.  For example, 'Jul 05'.
        Description
            String description of the event.
        '''
        self.date = date
        self.description = description


    def get_date( self ):
        '''
        Return the date for this event.
        '''
        return self.date


    def get_description( self ):
        '''
        Return the description for this event.
        '''
        return self.description


    def __str__( self ):
        return self.date + " | " + self.description


    def __repr__( self ):
        return self.__str__()


    def __eq__( self, other ):
        return (
            self.__class__ == other.__class__ and
            self.get_date() == other.get_date() and
            self.get_description() == other.get_description() )
