#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from tide import Reading, Type

import unittest


class Test( unittest.TestCase ):

    def testReading( self ):
        portID = "1234"
        year = 2021
        month = 11
        day = 22
        hour = 10
        minute = 30
        timezone = "+1030"
        levelInMetres = 1.23
        tideType = Type.H
        url = "http://www.url.com"

        myReading = Reading( portID, year, month, day, hour, minute, timezone, levelInMetres, tideType, url )

        self.assertAlmostEqual( myReading.getPortID(), portID )
        self.assertAlmostEqual( myReading.getYear(), year )
        self.assertAlmostEqual( myReading.getMonth(), month )
        self.assertAlmostEqual( myReading.getDay(), day  )
        self.assertAlmostEqual( myReading.getHour(), hour )
        self.assertAlmostEqual( myReading.getMinute(), minute )
        self.assertAlmostEqual( myReading.getTimezone(), timezone )
        self.assertAlmostEqual( myReading.getLevelInMetres(), levelInMetres )
        self.assertAlmostEqual( myReading.getType(), tideType )
        self.assertAlmostEqual( myReading.getURL(), url )

        self.assertAlmostEqual( myReading.__eq__( Reading( portID, year, month, day, hour, minute, timezone, levelInMetres, tideType, url ) ), True )

        self.assertAlmostEqual( myReading.__eq__( Reading( portID + " ", year, month, day, hour, minute, timezone, levelInMetres, tideType, url ) ), False )
        self.assertAlmostEqual( myReading.__eq__( Reading( portID, year + 1, month, day, hour, minute, timezone, levelInMetres, tideType, url ) ), False )
        self.assertAlmostEqual( myReading.__eq__( Reading( portID, year, month + 1, day, hour, minute, timezone, levelInMetres, tideType, url ) ), False )
        self.assertAlmostEqual( myReading.__eq__( Reading( portID, year, month, day + 1, hour, minute, timezone, levelInMetres, tideType, url ) ), False )
        self.assertAlmostEqual( myReading.__eq__( Reading( portID, year, month, day, hour + 1, minute, timezone, levelInMetres, tideType, url ) ), False )
        self.assertAlmostEqual( myReading.__eq__( Reading( portID, year, month, day, hour, minute + 1, timezone, levelInMetres, tideType, url ) ), False )
        self.assertAlmostEqual( myReading.__eq__( Reading( portID, year, month, day, hour, minute, timezone + " ", levelInMetres, tideType, url ) ), False )
        self.assertAlmostEqual( myReading.__eq__( Reading( portID, year, month, day, hour, minute, timezone, levelInMetres + 1.0, tideType, url ) ), False )
        self.assertAlmostEqual( myReading.__eq__( Reading( portID, year, month, day, hour, minute, timezone, levelInMetres, Type.L, url ) ), False )
        self.assertAlmostEqual( myReading.__eq__( Reading( portID, year, month, day, hour, minute, timezone, levelInMetres, tideType, url + " " ) ), False )

        readingString = \
            portID + " | " + \
            str( year ) + "-" + \
            str( month ) + "-" + \
            str( day ) + "-" + \
            str( hour ) + "-" + \
            str( minute ) + "-" + \
            str( timezone ) + " | " + \
            str( levelInMetres ) + " | " + \
            "H"

        self.assertAlmostEqual( myReading.__str__(), readingString )

        self.assertAlmostEqual( myReading.__repr__(), readingString )


if __name__ == '__main__':
    unittest.main()