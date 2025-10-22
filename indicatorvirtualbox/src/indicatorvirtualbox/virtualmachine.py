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


class VirtualMachine():
    ''' Information about a virtual machine. '''

    def __init__(
        self,
        name,
        uuid ):

        self.name = name
        self.uuid = uuid


    def get_name( self ):
        '''
        Return the name of this virtual machine.
        '''
        return self.name


    def get_uuid( self ):
        '''
        Return the UUID of this virtual machine.
        '''
        return self.uuid


    def __str__( self ):
        return self.get_name() + " | " + self.get_uuid()


    def __repr__( self ):
        return self.__str__()


    def __eq__(
        self,
        other ):

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
        '''
        Return the mame of this group.
        '''
        return self.name


    def add_item(
        self,
        virtual_machine_or_group ):
        '''
        Add virtual machine or group to this group.
        '''
        self.items.append( virtual_machine_or_group )


    def get_items( self ):
        '''
        Return the items within this group.
        '''
        return self.items


    def __str__( self ):
        return (
            self.get_name() + " [ " +
            ', '.join( [ x.__str__() for x in Group.sort( self.get_items() ) ] ) + " ]" )


    def __repr__( self ):
        return self.__str__()


    def __eq__(
        self,
        other ):

        return (
            self.__class__ == other.__class__
            and
            self.get_name() == other.get_name()
            and
            len( self.get_items() ) == len( other.get_items() )
            and
            self.get_items().__eq__( other.get_items() ) )


    @staticmethod
    def sort(
        items,
        sort_groups_and_virtual_machines_equally = False ):
        '''
        Sort virtual machines and groups.
        '''
        if sort_groups_and_virtual_machines_equally:
            sorted_items = (
                sorted(
                    items,
                    key = lambda x: locale.strxfrm( x.get_name() ) ) )

        else:
            sorted_items = (
                sorted(
                    items,
                    key = (
                        lambda x: (
                            not isinstance( x, Group ),
                            locale.strxfrm( x.get_name() ) ) ) ) )

        return sorted_items
