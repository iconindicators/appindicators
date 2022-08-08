#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from tide import Reading

import unittest


class Test( unittest.TestCase ):

    def testReading( self ):
        date = "Tuesday August 9"
        time = "5:40 am"
        location = "Fort Denison, Sydney, Australia"
        level = "1.25 m"
        isHigh = True
        url = "http://www.url.com"

        myReading = Reading( date, time, location, isHigh, level, url )

        self.assertAlmostEqual( myReading.getDate(), date )
        self.assertAlmostEqual( myReading.getTime(), time )
        self.assertAlmostEqual( myReading.getLocation(), location )
        self.assertAlmostEqual( myReading.isHigh(), isHigh )
        self.assertAlmostEqual( myReading.getLevel(), level )
        self.assertAlmostEqual( myReading.getURL(), url )

        self.assertAlmostEqual( myReading.__eq__( Reading( date, time, location,isHigh, level, url ) ), True )

        self.assertAlmostEqual( myReading.__eq__( Reading( date + " ", time, location, isHigh, level, url ) ), False )
        self.assertAlmostEqual( myReading.__eq__( Reading( date, time + " ", location, isHigh, level, url ) ), False )
        self.assertAlmostEqual( myReading.__eq__( Reading( date, time, location + " ", isHigh, level, url ) ), False )
        self.assertAlmostEqual( myReading.__eq__( Reading( date, time, location, not isHigh, level, url ) ), False )
        self.assertAlmostEqual( myReading.__eq__( Reading( date, time, location, isHigh, level + " ", url ) ), False )
        self.assertAlmostEqual( myReading.__eq__( Reading( date, time, location, isHigh, level, url + " " ) ), False )

        readingString = \
            date + " | " + \
            time + " | " + \
            location + " | " + \
            str( isHigh ) + " | " + \
            level + " | " + \
            url

        self.assertAlmostEqual( myReading.__str__(), readingString )

        self.assertAlmostEqual( myReading.__repr__(), readingString )


if __name__ == '__main__':
    unittest.main()