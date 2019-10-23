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


# Store a PPA's details and published binaries.


import operator


#TODO Find each 'set' function and determine why it is needed.
#Surely we only need the constructor and getters.

class PPA( object ):

    STATUS_ERROR_RETRIEVING_PPA = "ERROR RETRIEVING PPA"
    STATUS_MULTIPLE_ERRORS = "MULTIPLE ERRORS"
    STATUS_NEEDS_DOWNLOAD = "NEEDS DOWNLOAD"
    STATUS_NO_PUBLISHED_BINARIES = "NO PUBLISHED BINARIES"
    STATUS_OK = "OK"
    STATUS_PUBLISHED_BINARIES_COMPLETELY_FILTERED = "PUBLISHED BINARIES COMPLETELY FILTERED"


    def __init__( self, user, name, series, architecture ):
        self.status = PPA.STATUS_NEEDS_DOWNLOAD
        self.publishedBinaries = [ ]

        self.user = user
        self.name = name
        self.series = series
        self.architecture = architecture


    def getStatus( self ): return self.status


    def setStatus( self, status ):
#TODO Need to do the other stuff?  Maybe just set the status only?        
        if status == PPA.STATUS_OK:
            self.publishedBinaries.sort( key = operator.methodcaller( "__str__" ) )

        if status == PPA.STATUS_ERROR_RETRIEVING_PPA or \
           status == PPA.STATUS_MULTIPLE_ERRORS or \
           status == PPA.STATUS_NEEDS_DOWNLOAD or \
           status == PPA.STATUS_NO_PUBLISHED_BINARIES or \
           status == PPA.STATUS_PUBLISHED_BINARIES_COMPLETELY_FILTERED:
            self.publishedBinaries = [ ]

        self.status = status


    def getUser( self ): return self.user


    def getName( self ): return self.name


    def getSeries( self ): return self.series


    def getArchitecture( self ): return self.architecture


    # Used for combined PPAs.
    def nullifyArchitectureSeries( self ):
        self.architecture = None
        self.series = None


#TODO Who uses this?
    # Returns a key of the form 'PPA User | PPA Name | Series | Architecture' or 'PPA User | PPA Name' if series/architecture are undefined. 
    def getKey( self ):
        if self.series is None or self.architecture is None:
            key = str( self.user ) + " | " + str( self.name )

        else:
            key = str( self.user ) + " | " + str( self.name ) + " | " + str( self.series ) + " | " + str( self.architecture )

        return key


    def addPublishedBinary( self, publishedBinary ): self.publishedBinaries.append( publishedBinary )


    # Used for combined PPAs.
    def addPublishedBinaries( self, publishedBinaries ): self.publishedBinaries.extend( publishedBinaries )


    def getPublishedBinaries( self ): return self.publishedBinaries


    def sortPublishedBinariesByDownloadCountAndClip( self, clipAmount ):
        self.publishedBinaries.sort( key = operator.methodcaller( "getDownloadCount" ), reverse = True )
        if clipAmount > 0:
            del self.publishedBinaries[ clipAmount : ]


    def resetPublishedBinaries( self ): self.publishedBinaries = [ ]


    def __str__( self ): return str( self.__dict__ )


    def __repr__( self ): return self.__str__()


    def __eq__( self, other ): return self.__dict__ == other.__dict__


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


    def __str__( self ): return str( self.packageName ) + " | " + str( self.packageVersion ) + " | " + str( self.downloadCount ) + " | " + str( self.architectureSpecific )


    def __repr__( self ): return self.__str__()


    def __eq__( self, other ): return self.__dict__ == other.__dict__


#TODO Not sure if this will stay.
class Filter( object ):

    def __init__( self, user, name, filterText = [ ] ):
        self.user = user
        self.name = name
        self.filterText = filterText


    def getKey( self ): return self.user + " | " + self.name


    def __str__( self ): return str( self.user ) + " | " + str( self.name )


    def __repr__( self ): return self.__str__()


    def __eq__( self, other ): return self.__dict__ == other.__dict__