#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from ppa import PublishedBinary

import unittest


class Test( unittest.TestCase ):

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