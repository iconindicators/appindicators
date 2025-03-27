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

from copy import deepcopy
from enum import IntEnum
from functools import cmp_to_key


class PublishedBinary():
    '''
    Holds a published binary's name, version, architecture and download count.
    '''

    def __init__(
        self,
        name,
        version,
        architecture ):

        '''
        Name (string)
        Version (string)
        Architecture (None or string)
        Download count (integer)
        '''
        self.name = name
        self.version = version
        self.architecture = architecture
        self.download_count = 0


    def get_name( self ):
        return self.name


    def get_version( self ):
        return self.version


    def get_architecture( self ):
        return self.architecture


    def get_download_count( self ):
        return self.download_count


    def set_download_count(
        self,
        count ):

        self.download_count = count


    def __str__( self ):
        architecture = self.get_architecture()
        if architecture is None:
            architecture = ""

        return (
            self.get_name() + " | " +
            self.get_version() + " | " +
            architecture + " | " +
            str( self.get_download_count() ) )


    def __repr__( self ):
        return self.__str__()


    def __eq__( self, other ):
        return (
            self.__class__ == other.__class__ and
            self.get_name() == other.get_name() and
            self.get_version() == other.get_version() and
            self.get_architecture() == other.get_architecture() and
            self.get_download_count() == other.get_download_count() )


    @staticmethod
    def compare(
        published_binary1,
        published_binary2 ):
        '''
        Compare two Published Binaries by download count.
        If the download count is the same, sort by name then by version.
        '''

        if published_binary1.get_download_count() < published_binary2.get_download_count():
            sort_value = 1

        elif published_binary1.get_download_count() > published_binary2.get_download_count():
            sort_value = -1

        else:
            if published_binary1.get_name() < published_binary2.get_name():
                sort_value = -1

            elif published_binary1.get_name() > published_binary2.get_name():
                sort_value = 1

            else:
                if published_binary1.get_version() < published_binary2.get_version():
                    sort_value = -1

                elif published_binary1.get_version() > published_binary2.get_version():
                    sort_value = 1

                else:
                    sort_value = 0

        return sort_value


class PPA():
    ''' Specifies a PPA. '''

    class Status( IntEnum ):
        ''' Download status of a PPA. '''
        NEEDS_DOWNLOAD = 0
        OK = 1
        FILTERED = 2
        NO_PUBLISHED_BINARIES = 3
        ERROR_NETWORK = 4
        ERROR_OTHER = 5
        ERROR_TIMEOUT = 6


    def __init__(
        self,
        user,
        name ):

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


    def set_status(
        self,
        status ):

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


    def set_filters(
        self,
        filters ):

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


    def add_published_binary(
        self,
        published_binary ):

        self.published_binaries.append( published_binary )


    def has_published_binaries( self ):
        return len( self.published_binaries ) > 0


    def get_published_binaries( self ):
        return self.published_binaries


    def flush_published_binaries( self ):
        self.published_binaries = [ ]


    def has_status_error(
        self,
        ignore_other = False ):

        '''
        Returns True if the PPA has any of the error statuses.
        If ignore_other is set to True, the status of ERROR_OTHER is ignored.
        '''
        has_status_error = (
                self.get_status() == PPA.Status.ERROR_NETWORK
                or
                self.get_status() == PPA.Status.ERROR_TIMEOUT )

        if not ignore_other:
            has_status_error = (
                has_status_error
                or
                self.get_status() == PPA.Status.ERROR_OTHER )

        return has_status_error


    def __str__( self ):
        return (
            self.user + ' | ' +
            self.name + ' | ' +
            '[ ' + ' '.join( self.filters ) + ' ]' +
            str( self.published_binaries ) )


    def __repr__( self ):
        return self.__str__()


#TODO Test this.
    def __eq__( self, other ):
        return (
            self.__class__ == other.__class__
            and
            self.get_user() == other.get_user()
            and
            self.get_name() == other.get_name()
            and
            self.get_filters() == other.get_filters()
            and
            self.get_status() == other.get_status()
            and
            len( self.get_published_binaries() ) == len( other.get_published_binaries() )
            and
            self.get_published_binaries().__eq__( other.get_published_binaries() ) )


    @staticmethod
    def sort_ppas_by_user_then_name_then_published_binaries(
        ppas,
        sort_by_download,
        clip_amount ):

        '''
        Sort PPAs by name then user.

        For each PPA's published binaries:
            Sort by name then version (sort_by_download = False)
        or
            Sort by (reverse) download count then name, then version
             (sort_by_download = True)

        When sorting published binaries by download count, the published
        binaries may be truncated to an amount defined by clip_amount.
        When clip_amount is set to 0, no truncation occurs.

        When sorting published binaries by name, clip_amount is ignored.
        '''
        ppas_sorted = deepcopy( ppas )
        ppas_sorted.sort( key = cmp_to_key( PPA.compare_by_ppa ) )

        if sort_by_download:
            for ppa in ppas_sorted:
                ppa.get_published_binaries().sort(
                    key = cmp_to_key( PublishedBinary.compare ) )

                if clip_amount > 0:
                    del ppa.get_published_binaries()[ clip_amount : ]

        else:
            for ppa in ppas_sorted:
                ppa.get_published_binaries().sort(
                    key = operator.methodcaller( "__str__" ) )

        return ppas_sorted


    @staticmethod
    def compare_by_ppa(
        ppa1,
        ppa2 ):
        ''' Compare two PPAs by user, then by name. '''

        return (
            PPA.compare_by_user_and_name(
                ppa1.get_user(), ppa1.get_name(),
                ppa2.get_user(), ppa2.get_name() ) )


    @staticmethod
    def compare_by_user_and_name(
        user1,
        name1,
        user2,
        name2 ):
        ''' Compare two PPA users/names, by user, then by name. '''

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


    @staticmethod
    def identical(
        self,
        ppa1,
        ppa2 ):
        '''
        Returns true if both PPAs have the user, name and filters.
        '''

        return (
            PPA.compare_by_ppa( ppa1, ppa2 ) == 0
            and
            ppa1.get_filters() == ppa2.get_filters() )
