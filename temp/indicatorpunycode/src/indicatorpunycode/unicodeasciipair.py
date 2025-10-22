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


''' Comprises Unicode text and ASCII equivalent. '''


class UnicodeAsciiPair():
    ''' A single Unicode text and ASCII equivalent pair. '''

    def __init__(
        self,
        unicode_text,
        ascii_text ):

        self.unicode = unicode_text
        self.ascii = ascii_text


    def get_ascii( self ):
        '''
        Return the ASCII for this pair.
        '''
        return self.ascii


    def get_unicode( self ):
        '''
        Return the Unicode for this pair.
        '''
        return self.unicode


    def __str__( self ):
        return self.unicode + " | " + self.ascii


    def __repr__( self ):
        return self.__str__()


    def __eq__( self, other ):
        return (
            self.__class__ == other.__class__ and
            self.get_unicode() == other.get_unicode() and
            self.get_ascii() == other.get_ascii() )
