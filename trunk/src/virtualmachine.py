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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# Virtual Machine information.


class Info:

    # Name of VM or Group.
    # True if a group; False is a VM.
    # UUID of VM.
    # Numeric amount to indent when groups are used. 
    def __init__( self, name, isGroup, uuid, indent ):
        self.name = name
        self.group = isGroup
        self.uuid = uuid
        self.indent = indent


    def getName( self ): return self.name


    def setName( self, name ): self.name = name


    def isGroup( self ): return self.group


    def getUUID( self ): return self.uuid


    def getIndent( self ): return self.indent


    def getGroupName( self ): return self.name[ self.name.rfind( "/" ) + 1 : ] # Works for non-groups too, in case it's called!


    def __str__( self ): return self.getName() + " | " + str( self.isGroup() ) + " | " + self.getUUID() + " | " + str( self.getIndent() )


    def __repr__( self ): return self.__str__()