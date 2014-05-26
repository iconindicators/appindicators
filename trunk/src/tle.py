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


# Two-line Element Set.
# http://en.wikipedia.org/wiki/Two-line_element_set


class Info:

    def __init__( self, title, line1, line2 ):
        self.title = title
        self.line1 = line1
        self.line2 = line2


    def getName( self ): return self.title


    def getLine1( self ): return self.line1


    def getLine2( self ): return self.line2


    def getNumber( self ): return self.line1[ 2 : 7 ]


    def __str__( self ): return str( self.title ) + " | " + str( self.line1 ) + " | " + str( self.line2 )


    def __repr__( self ): return self.__str__()    