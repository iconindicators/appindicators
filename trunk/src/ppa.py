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


# Store a PPA's details and published binaries.


from enum import Enum

import operator


class PPA( object ):

    class Status( Enum ):
        ERROR_RETRIEVING_PPA = 0
        NEEDS_DOWNLOAD = 1
        NO_PUBLISHED_BINARIES = 2
        NO_PUBLISHED_BINARIES_AND_OR_COMPLETELY_FILTERED = 3
        OK = 4
        PUBLISHED_BINARIES_COMPLETELY_FILTERED = 5


    def __init__( self, user, name, series, architecture ):
        self.status = PPA.Status.NEEDS_DOWNLOAD
        self.publishedBinaries = [ ]

        self.user = user
        self.name = name
        self.series = series
        self.architecture = architecture


    def getStatus( self ): return self.status


    def setStatus( self, status ):
        self.status = status
        if not ( status == PPA.Status.OK ): # Any other status implies the underlying published binaries are reset.
            self.publishedBinaries = [ ]


    def getUser( self ): return self.user


    def getName( self ): return self.name


    def getSeries( self ): return self.series


    def getArchitecture( self ): return self.architecture


    # Returns a string description of the PPA of the form 'user | name | series | architecture'
    # or 'user | name' if series/architecture are undefined.
    def getDescriptor( self ):
        if self.series is None or self.architecture is None:
            descriptor = self.user + " | " + self.name

        else:
            descriptor = self.user + " | " + self.name + " | " + self.series + " | " + self.architecture

        return descriptor


    def addPublishedBinary( self, publishedBinary ):
        self.publishedBinaries.append( publishedBinary )


    def addPublishedBinaries( self, publishedBinaries ):
        self.publishedBinaries.extend( publishedBinaries )


    def getPublishedBinaries( self, sort = False ):
        if sort:
            self.publishedBinaries.sort( key = operator.methodcaller( "__str__" ) )

        return self.publishedBinaries


    def sortPublishedBinariesByDownloadCountAndClip( self, clipAmount ):
        self.publishedBinaries.sort( key = operator.methodcaller( "getDownloadCount" ), reverse = True )
        if clipAmount > 0:
            del self.publishedBinaries[ clipAmount : ]


    @staticmethod
    def sort( listOfPPAs ):
        listOfPPAs.sort( key = operator.methodcaller( "getDescriptor" ) )


    def __str__( self ):
        return self.user + " | " + \
               self.name + " | " + \
               str( self.series ) + " | " + \
               str( self.architecture ) + " | " + \
               self.publishedBinaries


    def __repr__( self ): return self.__str__()


#TODO Need and __eq__
        # return self.__class__ == event.__class__ and \


class PublishedBinary( object ):

    def __init__( self, packageName, packageVersion, downloadCount, architectureSpecific ):
        self.packageName = packageName
        self.packageVersion = packageVersion
        self.downloadCount = downloadCount
        self.architectureSpecific = architectureSpecific


    def getPackageName( self ): return self.packageName


    def getPackageVersion( self ): return self.packageVersion


    def setPackageVersion( self, packageVersion ): self.packageVersion = packageVersion


    def getDownloadCount( self ): return self.downloadCount


    def setDownloadCount( self, downloadCount ): self.downloadCount = downloadCount


    def isArchitectureSpecific( self ): return self.architectureSpecific


    def __str__( self ):
        return self.packageName + " | " + \
               str( self.packageVersion ) + " | " + \
               str( self.downloadCount ) + " | " + \
               str( self.architectureSpecific )


    def __repr__( self ): return self.__str__()


#TODO Need and __eq__
        # return self.__class__ == event.__class__ and \



class Filters( object ):

    INDEX_USER = 0
    INDEX_NAME = 1
    INDEX_SERIES = 2
    INDEX_ARCHITECTURE = 3


    def __init__( self ):
        self.filters = { }


    def addFilter( self, user, name, series, architecture, text = [ ] ):
        self.filters[ self.__getKey( user, name, series, architecture ) ] = text


    def hasFilter( self, user, name, series, architecture ):
        return self.__getKey( user, name, series, architecture ) in self.filters


    def getFilterText( self, user, name, series, architecture ):
        return self.filters[ self.__getKey( user, name, series, architecture ) ]


    def getUserNameSeriesArchitecture( self ):
        for key in sorted( self.filters.keys() ):
            keyComponents = key.split( " | " )
            yield keyComponents[ Filters.INDEX_USER ], keyComponents[ Filters.INDEX_NAME ], keyComponents[ Filters.INDEX_SERIES ], keyComponents[ Filters.INDEX_ARCHITECTURE ]


    def __getKey( self, user, name, series, architecture ):
        return user + " | " + name + " | " + series + " | " + architecture


    def __str__( self ): return str( self.__dict__ )


    def __repr__( self ): return self.__str__()


    def __eq__( self, filters ): return self.__dict__ == filters.__dict__#TODO Is this correct?