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


''' Virtual Machine information. '''


import operator


class VirtualMachine():
    ''' Information about a virtual machine. '''

    def __init__( self, name, uuid ):
        self.name = name
        self.uuid = uuid


    def get_name( self ):
        return self.name


    def get_uuid( self ):
        return self.uuid


    def __str__( self ):
        return self.get_name() + " | " + self.get_uuid()


    def __repr__( self ):
        return self.__str__()


    def __eq__( self, other ):
        return (
            self.__class__ == other.__class__ and
            self.get_name() == other.get_name() and
            self.get_uuid() == other.get_uuid() )


class Group():
    '''
    A group contains one or more groups and/or one or more virtual machines.
    '''

    def __init__( self, name ):
        self.name = name
        self.items = [ ] # Virtual machines and/or groups within this group.


    def get_name( self ):
        return self.name


    def add_item( self, virtual_machine_or_group ):
        self.items.append( virtual_machine_or_group )


    def get_items( self ):
        return self.items


    def __str__( self ):
        return (
            self.get_name() + ": " +
            ' | '.join( [ x.get_name() for x in self.get_items() ] ) )


    def __repr__( self ):
        return self.__str__()


    def __eq__( self, other ):
        equal = (
            self.__class__ == other.__class__ and
            self.get_name() == other.get_name() and
            len( self.get_items() ) == len( other.get_items( ) ) )

        if equal:
#TODO Remove \
            z = \
                zip(
                    sorted(
                        self.get_items(),
                        key = operator.methodcaller( "__str__" ) ),
                    sorted(
                        other.get_items(),
                        key = operator.methodcaller( "__str__" ) ) )

            for item_self, item_other in z:
                if not item_self.__eq__( item_other ):
                    equal = False
                    break

        return equal
