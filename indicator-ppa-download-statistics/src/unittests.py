#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from ppa import Filters, PPA, PublishedBinary

import unittest


class Test( unittest.TestCase ):

    def testFilters( self ):
        user = "user"
        name = "name"
        series = "series"
        architecture = "architecture"
        filterText = "filter text"

        myFilters = Filters()
        myOtherFilters = Filters()
        myOtherOtherFilters = Filters()

        self.assertAlmostEqual( myFilters.__eq__( myOtherFilters ), True )

        myFilters.addFilter( user, name, series, architecture )
        self.assertAlmostEqual( myFilters.getFilterText( user, name, series, architecture ), [ ] )

        self.assertAlmostEqual( myFilters.__eq__( myOtherFilters ), False )

        myOtherFilters.addFilter( user, name, series, architecture )
        self.assertAlmostEqual( myFilters.__eq__( myOtherFilters ), True )

        myOtherOtherFilters.addFilter( user + " ", name, series, architecture )
        self.assertAlmostEqual( myFilters.__eq__( myOtherOtherFilters ), False )

        self.assertAlmostEqual( myFilters.hasFilter( user, name, series, architecture ), True )
        self.assertAlmostEqual( myFilters.hasFilter( user + " ", name, series, architecture ), False )

        myFilters.addFilter( user, name, series, architecture, filterText )
        self.assertAlmostEqual( myFilters.getFilterText( user, name, series, architecture ), filterText )

        for u, n, s, a in myFilters.getUserNameSeriesArchitecture():
            self.assertAlmostEqual( u, user )
            self.assertAlmostEqual( n, name )
            self.assertAlmostEqual( s, series )
            self.assertAlmostEqual( a, architecture )

        filtersString = \
            "{'filters': {'" + \
             user + " | " + \
             name + " | " + \
             series + " | " + \
             architecture + \
             "': '" + \
             filterText + \
             "'}}"

        self.assertAlmostEqual( myFilters.__str__(), filtersString )
        
        self.assertAlmostEqual( myFilters.__repr__(), filtersString )


    def testPublisedBinary( self ):
        packageName = "package name"
        packageVersion = "1.2.3.4"
        downloadCount = "666"
        architectureSpecific = "false"

        myPublishedBinary = PublishedBinary( packageName, packageVersion, downloadCount, architectureSpecific )

        self.assertAlmostEqual( myPublishedBinary.getPackageName(), packageName )
        self.assertAlmostEqual( myPublishedBinary.getPackageVersion(), packageVersion )
        self.assertAlmostEqual( myPublishedBinary.getDownloadCount(), downloadCount )
        self.assertAlmostEqual( myPublishedBinary.isArchitectureSpecific(), architectureSpecific )

        self.assertAlmostEqual( myPublishedBinary.__eq__( PublishedBinary( packageName, packageVersion, downloadCount, architectureSpecific ) ), True )
        self.assertAlmostEqual( myPublishedBinary.__eq__( PublishedBinary( packageName + " ", packageVersion, downloadCount, architectureSpecific ) ), False )
        self.assertAlmostEqual( myPublishedBinary.__eq__( PublishedBinary( packageName, packageVersion + " ", downloadCount, architectureSpecific ) ), False )
        self.assertAlmostEqual( myPublishedBinary.__eq__( PublishedBinary( packageName, packageVersion, downloadCount + " ", architectureSpecific ) ), False )
        self.assertAlmostEqual( myPublishedBinary.__eq__( PublishedBinary( packageName, packageVersion, downloadCount, "true" ) ), False )

        publishedBinaryString = \
            packageName + " | " + \
            packageVersion + " | " + \
            downloadCount + " | " + \
            architectureSpecific

        self.assertAlmostEqual( myPublishedBinary.__str__(), publishedBinaryString )

        self.assertAlmostEqual( myPublishedBinary.__repr__(), publishedBinaryString )


    def testPPA( self ):
        user = "user"
        name = "name"
        series = "series"
        architecture = "architecture"

        myPPA = PPA( user, name, series, architecture )

        self.assertAlmostEqual( myPPA.getUser(), user )
        self.assertAlmostEqual( myPPA.getName(), name )
        self.assertAlmostEqual( myPPA.getSeries(), series )
        self.assertAlmostEqual( myPPA.getArchitecture(), architecture )
        self.assertAlmostEqual( myPPA.getStatus(), PPA.Status.NEEDS_DOWNLOAD )

        myPPA.setStatus( PPA.Status.ERROR_RETRIEVING_PPA )
        self.assertAlmostEqual( myPPA.getStatus(), PPA.Status.ERROR_RETRIEVING_PPA )

        descriptor = user + " | " + name + " | " + series + " | " + architecture
        self.assertAlmostEqual( myPPA.getDescriptor(), descriptor)

        packageName = "package name"
        packageVersion = "1.2.3.4"
        downloadCount = "666"
        architectureSpecific = "false"

        myPublishedBinary = PublishedBinary( packageName, packageVersion, downloadCount, architectureSpecific )
        myPPA = PPA( user, name, series, architecture )
        myPPA.addPublishedBinary( myPublishedBinary )

        self.assertAlmostEqual( myPPA.getPublishedBinaries(), [ myPublishedBinary ] )

        myOtherPPA = PPA( user, name, series, architecture )
        myOtherPPA.addPublishedBinary( PublishedBinary( packageName, packageVersion, downloadCount, architectureSpecific ) ) 
        self.assertAlmostEqual( myPPA.__eq__( myOtherPPA ), True )
        myOtherPPA.addPublishedBinary( PublishedBinary( packageName, packageVersion, downloadCount, "true" ) ) 
        self.assertAlmostEqual( myPPA.__eq__( myOtherPPA ), False )


if __name__ == '__main__':
    unittest.main()