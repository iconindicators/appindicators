#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import datetime, stardate, unittest


class Test( unittest.TestCase ):

    def testGregorianToStardateClassic( self ):

        self.assertRaises( Exception, stardate.getStardateClassic, datetime.datetime.fromisoformat( "1899-12-31 00:00:00" ) )

        stardateIssue, stardateInteger, stardateFraction = stardate.getStardateClassic( datetime.datetime.fromisoformat( "2162-01-04 00:00:00" ) )
        self.assertAlmostEqual( stardateIssue, 0 )
        self.assertAlmostEqual( stardateInteger, 0 )
        self.assertAlmostEqual( stardateFraction, 0 )

        stardateIssue, stardateInteger, stardateFraction = stardate.getStardateClassic( datetime.datetime.fromisoformat( "2270-01-26 00:00:00" ) )
        self.assertAlmostEqual( stardateIssue, 19 )
        self.assertAlmostEqual( stardateInteger, 7340 )
        self.assertAlmostEqual( stardateFraction, 0 )

        stardateIssue, stardateInteger, stardateFraction = stardate.getStardateClassic( datetime.datetime.fromisoformat( "2283-10-05 00:00:00" ) )
        self.assertAlmostEqual( stardateIssue, 19 )
        self.assertAlmostEqual( stardateInteger, 7840 )
        self.assertAlmostEqual( stardateFraction, 0 )

        stardateIssue, stardateInteger, stardateFraction = stardate.getStardateClassic( datetime.datetime.fromisoformat( "2323-01-01 00:00:00" ) )
        self.assertAlmostEqual( stardateIssue, 21 )
        self.assertAlmostEqual( stardateInteger, 0 )
        self.assertAlmostEqual( stardateFraction, 0 )

        self.assertRaises( Exception, stardate.getStardateClassic, datetime.datetime.fromisoformat( "9501-01-01 00:00:00" ) )


    # Reference: https://en.wikipedia.org/wiki/Stardate
    def testGregorianToStardate2009Revised( self ):

        self.assertRaises( Exception, stardate.getStardate2009Revised, datetime.datetime.fromisoformat( "1899-12-31 00:00:00" ) )

        stardateInteger, stardateFraction = stardate.getStardate2009Revised( datetime.datetime.fromisoformat( "2258-02-11 00:00:00" ) )
        self.assertAlmostEqual( stardateInteger, 2258 )
        self.assertAlmostEqual( stardateFraction, 42 )

        stardateInteger, stardateFraction = stardate.getStardate2009Revised( datetime.datetime.fromisoformat( "2259-02-24 00:00:00" ) )
        self.assertAlmostEqual( stardateInteger, 2259 )
        self.assertAlmostEqual( stardateFraction, 55 )

        stardateInteger, stardateFraction = stardate.getStardate2009Revised( datetime.datetime.fromisoformat( "2263-01-02 00:00:00" ) )
        self.assertAlmostEqual( stardateInteger, 2263 )
        self.assertAlmostEqual( stardateFraction, 2 )

        self.assertRaises( Exception, stardate.getStardate2009Revised, datetime.datetime.fromisoformat( "9501-01-01 00:00:00" ) )


    def testGregorianFromStardateClassic( self ):

        self.assertRaises( Exception, stardate.getGregorianFromStardateClassic, 19, 10000, 0 )
        self.assertRaises( Exception, stardate.getGregorianFromStardateClassic, 20, 5006, 0 )
        self.assertRaises( Exception, stardate.getGregorianFromStardateClassic, 21, 100000, 0 )
        self.assertRaises( Exception, stardate.getGregorianFromStardateClassic, 19, 0, -1 )

        dateTime = stardate.getGregorianFromStardateClassic( 0, 0, 0 )
        self.assertAlmostEqual( dateTime.year, 2162 )
        self.assertAlmostEqual( dateTime.month, 1 )
        self.assertAlmostEqual( dateTime.day, 4 )

        dateTime = stardate.getGregorianFromStardateClassic( 19, 7340, 0 )
        self.assertAlmostEqual( dateTime.year, 2270 )
        self.assertAlmostEqual( dateTime.month, 1 )
        self.assertAlmostEqual( dateTime.day, 26 )

        dateTime = stardate.getGregorianFromStardateClassic( 19, 7840, 0 )
        self.assertAlmostEqual( dateTime.year, 2283 )
        self.assertAlmostEqual( dateTime.month, 10 )
        self.assertAlmostEqual( dateTime.day, 5 )
        
        dateTime = stardate.getGregorianFromStardateClassic( 21, 1, 1 )
        self.assertAlmostEqual( dateTime.year, 2323 )
        self.assertAlmostEqual( dateTime.month, 1 )
        self.assertAlmostEqual( dateTime.day, 1 )


    def testGregorianFromStardate2009Revised( self ):

        self.assertRaises( Exception, stardate.getGregorianFromStardate2009Revised, 0, -1 )
        self.assertRaises( Exception, stardate.getGregorianFromStardate2009Revised, 2000, 367 )
        self.assertRaises( Exception, stardate.getGregorianFromStardate2009Revised, 2001, 366 )

        dateTime = stardate.getGregorianFromStardate2009Revised( 2258, 42 )
        self.assertAlmostEqual( dateTime.year, 2258 )
        self.assertAlmostEqual( dateTime.month, 2 )
        self.assertAlmostEqual( dateTime.day, 11 )

        dateTime = stardate.getGregorianFromStardate2009Revised( 2259, 55 )
        self.assertAlmostEqual( dateTime.year, 2259 )
        self.assertAlmostEqual( dateTime.month, 2 )
        self.assertAlmostEqual( dateTime.day, 24 )

        dateTime = stardate.getGregorianFromStardate2009Revised( 2263, 2 )
        self.assertAlmostEqual( dateTime.year, 2263 )
        self.assertAlmostEqual( dateTime.month, 1 )
        self.assertAlmostEqual( dateTime.day, 2 )


if __name__ == '__main__':
    unittest.main()