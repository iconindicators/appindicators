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


'''
A fortune comprises a summary and a message, used to be shown in the on-screen
notification.
'''


class Fortune():
    ''' A fortune message and summary. '''

    def __init__(
        self,
        message,
        summary ):
        '''
        Description
            Result of calling `fortune`.
            On error, a relevant error message.
        Summary
            User defined string to be shown in a on-screen notification.
            On error calling 'fortune', a short string indicating an error has
            occurred.
        '''
        self.message = message
        self.summary = summary


    def get_message( self ):
        return self.message


    def get_summary( self ):
        return self.summary


    def __str__( self ):
        return self.summary + " | " + self.message


    def __repr__( self ):
        return self.__str__()


    def __eq__( self, other ):
        return (
            self.__class__ == other.__class__ and
            self.get_message() == other.get_message() and
            self.get_summary() == other.get_summary() )
