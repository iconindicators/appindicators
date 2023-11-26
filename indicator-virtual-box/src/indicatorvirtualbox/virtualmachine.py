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


# Virtual Machine information.


class VirtualMachine( object ):

    def __init__( self, name, uuid ):
        self.name = name
        self.uuid = uuid


    def getName( self ):
        return self.name


    def getUUID( self ):
        return self.uuid


    def __str__( self ):
        return self.getName() + " | " + self.getUUID()


    def __repr__( self ):
        return self.__str__()


    def __eq__( self, other ):
        return \
            self.__class__ == other.__class__ and \
            self.getName() == other.getName() and \
            self.getUUID() == other.getUUID()


class Group( object ):

    def __init__( self, name ):
        self.name = name
        self.items = [ ] # List of virtual machines and/or groups pertaining to this group.


    def getName( self ):
        return self.name


    def addItem( self, virtualMachineOrGroup ):
        self.items.append( virtualMachineOrGroup )


    def getItems( self ):
        return self.items


    def __str__( self ):
        return self.getName() + ": " + ' | '.join( [ str( x.getName() ) for x in self.getItems() ] )


    def __repr__( self ):
        return self.__str__()


    def __eq__( self, other ):
        equal = \
            self.__class__ == other.__class__ and \
            self.getName() == other.getName() and \
            len( self.getItems() ) == len( other.getItems( ) )

        if equal:
            for itemFromSelf, itemFromOther in zip( self.getItems(), other.getItems() ):
                equal &= itemFromSelf.__eq__( itemFromOther )

        return equal