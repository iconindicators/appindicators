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


class Filter():
    ''' A filter screens out unwanted PPAs on download. '''


#TODO Delete
    # INDEX_USER = 0
    # INDEX_NAME = 1
    # INDEX_TEXT = 2


    def __init__( self, user, name, text ):
        self.user = user
        self.name = name
        self.text = text


    def get_user( self ):
        return self.user


    def get_name( self ):
        return self.name


    def get_text( self ):
        return self.text


#TODO Delete
#    def add_filter( self, user, name, text = None ):
#        self.filters[ self._get_key( user, name ) ] = text


#TODO Make this a static version if needed.
#TODO Delete
#    def has_filter( self, user, name ):
#        return self._get_key( user, name ) in self.filters


#TODO Delete
#    def get_filter_text( self, user, name ):
#        return self.filters[ self._get_key( user, name ) ]


#TODO Delete
#    def get_user_name( self ):
#        for key in sorted( self.filters.keys() ):
#            key_components = key.split( " | " )
#            # yield \
#            #     key_components[ Filters.INDEX_USER ], \
#            #     key_components[ Filters.INDEX_NAME ]


#TODO Delete
#    def _get_key( self, user, name, ):
#        return user + " | " + name


    def __str__( self ):
        return (
            self.user + " | " +
            self.name + " | " +
            self.text )


    def __repr__( self ):
        return self.__str__()


    def __eq__( self, other ):
        return \
            self.__class__ == other.__class__ and \
            self.get_user() == other.get_user() and \
            self.get_name() == other.get_name() and \
            self.get_text() == other.get_text()


class PublishedBinary():
    ''' PPA downloaded data. '''

    def __init__(
            self,
            package_name,
            package_version,
            download_count,
            architecture_specific ):
        '''
        Package name, package version (string)
        Download count (integer)
        Architecture specific (boolean)
        '''

        self.package_name = package_name
        self.package_version = package_version
        self.download_count = download_count
        self.architecture_specific = architecture_specific


    def get_package_name( self ):
        return self.package_name


    def get_package_version( self ):
        return self.package_version


    def get_download_count( self ):
        return self.download_count


    def is_architecture_specific( self ):
        return self.architecture_specific


#TODO Check the comment below after combine is sorted.
    def __str__( self ):
        # Requires str() as None will be returned when
        # published binaries are combined.
        return (
            self.get_package_name() + " | " +
            str( self.get_package_version() ) + " | " +
            str( self.get_download_count() ) + " | " +
            str( self.is_architecture_specific() ) )


    def __repr__( self ):
        return self.__str__()


    def __eq__( self, other ):
        return \
            self.__class__ == other.__class__ and \
            self.get_package_name() == other.get_package_name() and \
            self.get_package_version() == other.get_package_version() and \
            self.get_download_count() == other.get_download_count() and \
            self.is_architecture_specific() == other.is_architecture_specific()


class PPA():
    ''' Specifies a PPA. '''

    class Status( Enum ):
        ''' Download status of a PPA. '''
        NEEDS_DOWNLOAD = 0
        ERROR_RETRIEVING_PPA = 1
        OK = 2
        NO_PUBLISHED_BINARIES = 3
        FILTERED = 4
        MIX_OF_OK_NO_PUBLISHED_BINARIES_FILTERED = 5


    def __init__( self, user, name, series, architecture ):
        self.status = PPA.Status.NEEDS_DOWNLOAD
        self.published_binaries = [ ]

        self.user = user
        self.name = name
        self.series = series
        self.architecture = architecture


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


    def get_series( self ):
        return self.series


    def get_architecture( self ):
        return self.architecture


    # Returns a string description of the PPA of the form
    #   user | name | series | architecture
    # or
    #   user | name
    # if series/architecture are undefined.
    def get_descriptor( self ):
        descriptor = self.user + ' | ' + self.name
        if self.series is not None and self.architecture is not None:
            descriptor += ' | ' + self.series + ' | ' + self.architecture

        return descriptor


    def add_published_binary( self, published_binary ):
        self.published_binaries.append( published_binary )


#TODO Is this used?
#    def add_published_binaries( self, published_binaries ):
#        self.published_binaries.extend( published_binaries )


    def has_published_binaries( self ):
        return len( self.published_binaries ) > 0


#TODO When would we NOT want to sort?
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
    def sort( list_of_ppas ):
        list_of_ppas.sort(
            key = operator.methodcaller( "get_descriptor" ) )


    def __str__( self ):
        return (
            self.user + ' | ' +
            self.name + ' | ' +
            str( self.series ) + ' | ' +
            str( self.architecture ) + ' | ' +
            str( self.published_binaries ) )


    def __repr__( self ):
        return self.__str__()


    def __eq__( self, other ):
        equal = \
            self.__class__ == other.__class__ and \
            self.get_user() == other.get_user() and \
            self.get_name() == other.get_name() and \
            self.get_series() == other.get_series() and \
            self.get_architecture() == other.get_architecture() and \
            self.get_status() == other.get_status() and \
            len( self.get_published_binaries() ) == len( other.get_published_binaries() )

        if equal:
            for \
                published_binary_self, published_binary_other in \
                zip( self.get_published_binaries(), other.get_published_binaries() ):

                equal &= published_binary_self.__eq__( published_binary_other )

        return equal
