#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from ppa import Filters, PublishedBinary

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

        # for u, n, s, a in myFilters.getUserNameSeriesArchitecture():
        #     self.assertAlmostEqual( myFilters.getFilterText( user, name, series, architecture ), filterText )
        #     print( a, b, c, d )

        # self.assertAlmostEqual( myPublishedBinary.getPackageName(), packageName )
        # self.assertAlmostEqual( myPublishedBinary.getPackageVersion(), packageVersion )
        # self.assertAlmostEqual( myPublishedBinary.getDownloadCount(), downloadCount )
        # self.assertAlmostEqual( myPublishedBinary.isArchitectureSpecific(), architectureSpecific )
        #
        # self.assertAlmostEqual( myPublishedBinary.__eq__( PublishedBinary( packageName, packageVersion, downloadCount, architectureSpecific ) ), True )
        # self.assertAlmostEqual( myPublishedBinary.__eq__( PublishedBinary( packageName + " ", packageVersion, downloadCount, architectureSpecific ) ), False )
        # self.assertAlmostEqual( myPublishedBinary.__eq__( PublishedBinary( packageName, packageVersion + " ", downloadCount, architectureSpecific ) ), False )
        # self.assertAlmostEqual( myPublishedBinary.__eq__( PublishedBinary( packageName, packageVersion, downloadCount + " ", architectureSpecific ) ), False )
        # self.assertAlmostEqual( myPublishedBinary.__eq__( PublishedBinary( packageName, packageVersion, downloadCount, "true" ) ), False )
        #
        # publishedBinaryString = \
        #     packageName + " | " + \
        #     packageVersion + " | " + \
        #     downloadCount + " | " + \
        #     architectureSpecific
        #
        # self.assertAlmostEqual( myPublishedBinary.__str__(), publishedBinaryString )
        #
        # self.assertAlmostEqual( myPublishedBinary.__repr__(), publishedBinaryString )


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


if __name__ == '__main__':
    unittest.main()