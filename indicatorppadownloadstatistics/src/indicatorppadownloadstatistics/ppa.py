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


''' Store a PPA's user, name, filters and published binaries. '''


import locale
import operator

from enum import Enum
from functools import cmp_to_key


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


    def __str__( self ):
        print( "pb str" )#TODO Test
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
        OK = 1
        FILTERED = 2
        NO_PUBLISHED_BINARIES = 3
        ERROR_NETWORK = 4
        ERROR_OTHER = 5
        ERROR_TIMEOUT = 6


    def __init__( self, user, name ):
        '''
        Creates a PPA with a default single filter [ "" ].

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
        if not status == PPA.Status.OK:
            self.published_binaries = [ ]


    def get_user( self ):
        return self.user


    def get_name( self ):
        return self.name


    def get_filters( self ):
        ''' Returns the list of filter strings. '''
        return self.filters


    def set_filters( self, filters ):
        '''
        Set a list of one or more filter strings.
        Each filter string must be plain text without whitespace.
        '''
        self.filters = filters


    def has_default_filter( self ):
        ''' Returns True if only the default filter of [ "" ] exists. '''
        return len( self.filters ) == 1 and self.filters[ 0 ] == ''


    def get_descriptor( self ):
        return self.user + ' | ' + self.name


    def add_published_binary( self, published_binary ):
        self.published_binaries.append( published_binary )


    def has_published_binaries( self ):
        return len( self.published_binaries ) > 0


    def get_published_binaries( self ):
        return self.published_binaries


#TODO Hopefully can delete
    # def get_published_binaries_sorted( self ):
    #     self.published_binaries.sort(
    #         key = operator.methodcaller( "__str__" ) )
    #
    #     return self.published_binaries


    def flush_published_binaries( self ):
        self.published_binaries = [ ]


#TODO Hopefully can delete
    # def sort_published_binaries_by_download_count_and_clip( self, clip_amount ):
    #     self.published_binaries.sort(
    #         key = operator.methodcaller( "get_download_count" ),
    #         reverse = True )
    #
    #     if clip_amount > 0:
    #         del self.published_binaries[ clip_amount : ]


    @staticmethod
    def sort_ppas_by_user_then_name_then_published_binaries(
            ppas, sort_by_download, clip_amount ):

        ppas_sorted = sorted( ppas, key = cmp_to_key( PPA.__compare ) )

        if sort_by_download:
            for ppa in ppas_sorted:
                ppa.get_published_binaries().sort(
                    key = operator.methodcaller( "get_download_count" ),
                    reverse = True )

                if clip_amount > 0:
                    del ppa.get_published_binaries()[ clip_amount : ]

        else:
            for ppa in ppas_sorted:
                ppa.get_published_binaries().sort(
                    key = operator.methodcaller( "__str__" ) )

        return ppas_sorted


    @staticmethod
    def __compare( ppa1, ppa2 ):
        ''' Compare two PPAs, first by user, then by name. '''
        return \
            PPA.compare(
                ppa1.get_user(), ppa1.get_name(),
                ppa2.get_user(), ppa2.get_name() )


    @staticmethod
    def compare( user1, name1, user2, name2 ):
        ''' Compare two PPAs, first by user, then by name. '''
        user1_ = locale.strxfrm( user1 )
        user2_ = locale.strxfrm( user2 )
        if user1_ < user2_:
            sort_value = -1

        elif user1_ > user2_:
            sort_value = 1

        else:
            name1_ = locale.strxfrm( name1 )
            name2_ = locale.strxfrm( name2 )
            if name1_ < name2_:
                sort_value = -1

            elif name1_ > name2_:
                sort_value = 1

            else:
                sort_value = 0

        return sort_value


    def __str__( self ):
        print( "ppa str" )#TODO Test
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
