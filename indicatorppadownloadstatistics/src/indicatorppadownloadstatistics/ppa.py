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


""" Store a PPA's details, published binaries and filters. """


import operator

from enum import Enum


class PublishedBinary():
    ''' PPA downloaded data. '''

    def __init__( self, name, version, architecture_specific, download_count ):
        '''
        Name (string)
        Version (string)
        Architecture specific (boolean) 
        Download count (integer)
        '''

        self.name = name
        self.version = version
        self.architecture_specific = architecture_specific
        self.download_count = download_count


    def get_name( self ):
        return self.name


    def get_version( self ):
        return self.version


    def get_architecture_specific( self ):
        return self.architecture_specific


    def get_download_count( self ):
        return self.download_count


    def set_download_count( self, count ):
        self.download_count = count


#TODO Check this works.
    def __str__( self ):
        return (
            self.get_name() + " | " +
            self.get_version() + " | " +
            str( self.get_architecture_specific() ) + " | " +
            str( self.get_download_count() ) )


    def __repr__( self ):
        return self.__str__()


    def __eq__( self, other ):
        return \
            self.__class__ == other.__class__ and \
            self.get_name() == other.get_name() and \
            self.get_version() == other.get_version() and \
            self.get_architecture_specific() == other.get_architecture_specific() and \
            self.get_download_count() == other.get_download_count()


class PPA():
    ''' Specifies a PPA. '''

    class Status( Enum ):
        ''' Download status of a PPA. '''
        NEEDS_DOWNLOAD = 0
        ERROR_RETRIEVING_PPA = 1
        OK = 2
        NO_PUBLISHED_BINARIES = 3
        FILTERED = 4


    def __init__( self, user, name ):
        '''
        User (string)
        Name (string)
        '''
        self.user = user
        self.name = name
        self.filters = [ "" ]
        self.published_binaries = [ ]
        self.status = PPA.Status.NEEDS_DOWNLOAD


    def get_status( self ):
        return self.status


    def set_status( self, status ):
        self.status = status
        if not status == PPA.Status.OK: # Any other status implies the underlying published binaries are reset.   #TODO What does this mean????
            self.published_binaries = [ ]


    def get_user( self ):
        return self.user


    def get_name( self ):
        return self.name


    def get_filters( self ):
        '''
        Returns a list of strings, each of which is a filter.
        When no filters have been added, the list contains a single empty string.
        '''
        return self.filters


    def set_filters( self, filters ):
        self.filters = filters


    def get_descriptor( self ):
        return self.user + ' | ' + self.name


    def add_published_binary( self, published_binary ):
        self.published_binaries.append( published_binary )


    def has_published_binaries( self ):
        return len( self.published_binaries ) > 0


#TODO When would we NOT want to sort?
# Sorting is used when combining...
    def get_published_binaries( self, sort = False ):
        if sort:
            self.published_binaries.sort(
                key = operator.methodcaller( "__str__" ) )

        return self.published_binaries


    def flush_published_binaries( self ):
        self.published_binaries = [ ]


    def sort_published_binaries_by_download_count_and_clip(
        self, clip_amount ):

        self.published_binaries.sort(
            key = operator.methodcaller( "get_download_count" ),
            reverse = True )

        if clip_amount > 0:
            del self.published_binaries[ clip_amount : ]


    @staticmethod
#TODO This is called at the end of combine...where else?
# Now that combine is gone, is this still used?
    def sort( list_of_ppas ):
        list_of_ppas.sort(
            key = operator.methodcaller( "get_descriptor" ) )


#TODO Check this works.
    def __str__( self ):
        return (
            self.user + ' | ' +
            self.name + ' | ' +
            '[ ' + ' '.join( self.filters ) + ' ]' +
            str( self.published_binaries ) )


    def __repr__( self ):
        return self.__str__()


    def __eq__( self, other ):
        equal = \
            self.__class__ == other.__class__ and \
            self.get_user() == other.get_user() and \
            self.get_name() == other.get_name() and \
            self.get_filters() == other.get_filters() and \
            self.get_status() == other.get_status() and \
            len( self.get_published_binaries() ) == len( other.get_published_binaries() )

        if equal:
            for \
                published_binary_self, published_binary_other in \
                zip( self.get_published_binaries(), other.get_published_binaries() ):

                equal &= published_binary_self.__eq__( published_binary_other )

        return equal
