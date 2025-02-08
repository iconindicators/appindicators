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


import locale
import operator


class VirtualMachine():
    ''' Information about a virtual machine. '''

    def __init__(
        self,
        name,
        uuid ):

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

    def __init__(
        self,
        name ):

        self.name = name
        self.items = [ ] # Virtual machines and/or groups within this group.


    def get_name( self ):
        return self.name


    def add_item(
        self,
        virtual_machine_or_group ):

        self.items.append( virtual_machine_or_group )


    def get_items( self ):
        return self.items


    @staticmethod
    def sort(
        items,
        sort_groups_and_virtual_machines_equally = False ):

        if sort_groups_and_virtual_machines_equally:
            sorted_items = (
                sorted(
                    items,
                    key = lambda x: locale.strxfrm( x.get_name() ) ) )

        else:
            sorted_items = (
                sorted(
                    items,
                    key = lambda x: (
                        not isinstance( x, Group ),
                        locale.strxfrm( x.get_name() ) ) ) )

        return sorted_items


    def __str__( self ):


        # s = self.get_name() + " [\n\t"
        #
        # for x in [ x.__str__() for x in Group.sort( self.get_items() ) ]:
        #     if isinstance( x, Group ):
        #         s += x + "\n\t"
        #
        #     else:
        #         s += x + ",\n\t"
        #
        # return s
            
        return (
            self.get_name() + " [ " +
            ', '.join( [ x.__str__() for x in Group.sort( self.get_items() ) ] ) + " ]" )


        # def _string( items ):
        #     s = ""
        #     for item in items:
        #         if isinstance( item, Group ):
        #             s += (
        #                 item.get_name()
        #                 +
        #                 " [ "
        #                 +
        #                 _string( Group.sort( item.get_items() ) )
        #                 +
        #                 " ], " )
        #
        #         else:
        #             s += item.__str__() + ', '
        #
        #     if s[ -1 ] == ' ' and s[ -2 ] == ',':
        #         s = s[ 0 : -2 ]
        #
        #     return s
        #
        #
        # return (
        #     self.get_name()
        #     +
        #     " [ "
        #     +
        #     _string( Group.sort( self.get_items() ) )
        #     +
        #     " ]" )


    def __repr__( self ):
        return self.__str__()


#TODO This needs to use recursion or something as only one level of groups is handled (does not handle nesting).
# Perhaps could get away with checking all classes deeply and then if that is fine,
# __str__ each and compare.
    def __eq__( self, other ):
        equal = (
            self.__class__ == other.__class__ and
            self.get_name() == other.get_name() and
            len( self.get_items() ) == len( other.get_items( ) ) )

        if equal:
            z = (
                zip(
                    sorted(
                        self.get_items(),
                        key = operator.methodcaller( "__str__" ) ),
                    sorted(
                        other.get_items(),
                        key = operator.methodcaller( "__str__" ) ) ) )

            for item_self, item_other in z:
                if not item_self.__eq__( item_other ):
                    equal = False
                    break

        return equal
