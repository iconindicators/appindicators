#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from orbitalelement import OE
from twolineelement import TLE

import unittest


class Test( unittest.TestCase ):

    def testOE( self ):

        name = "name"
        data = "1 2 3 4"
        dataType = OE.DataType.SKYFIELD_COMET

        myOrbitalElement = OE( name, data, dataType )

        self.assertAlmostEqual( myOrbitalElement.getName(), name )
        self.assertAlmostEqual( myOrbitalElement.getData(), data )
        self.assertAlmostEqual( myOrbitalElement.getDataType(), dataType )

        self.assertAlmostEqual( myOrbitalElement.__eq__( OE( name, data, dataType ) ), True )
        self.assertAlmostEqual( myOrbitalElement.__eq__( OE( name + " ", data, dataType ) ), False )
        self.assertAlmostEqual( myOrbitalElement.__eq__( OE( name, data + " ", dataType ) ), False )
        self.assertAlmostEqual( myOrbitalElement.__eq__( OE( name, data, OE.DataType.SKYFIELD_MINOR_PLANET ) ), False )

        self.assertAlmostEqual( myOrbitalElement.__str__(), data )
        
        self.assertAlmostEqual( myOrbitalElement.__repr__(), data )


    def testTLE( self ):

        title = "title"
        line1 = "1 2 3 4"
        line2 = "5 6 7 8"

        myTwoLineElement = TLE( title, line1, line2 )

        self.assertAlmostEqual( myTwoLineElement.getTitle(), title )
        self.assertAlmostEqual( myTwoLineElement.getLine1(), line1 )
        self.assertAlmostEqual( myTwoLineElement.getLine2(), line2 )

        self.assertAlmostEqual( myTwoLineElement.__eq__( TLE( title, line1, line2 ) ), True )
        self.assertAlmostEqual( myTwoLineElement.__eq__( TLE( title + " ", line1, line2 ) ), False )
        self.assertAlmostEqual( myTwoLineElement.__eq__( TLE( title, line1 + " ", line2 ) ), False )
        self.assertAlmostEqual( myTwoLineElement.__eq__( TLE( title, line1, line2 + " " ) ), False )

        twoLineElementString = \
            title + " | " + \
            line1 + " | " + \
            line2

        self.assertAlmostEqual( myTwoLineElement.__str__(), twoLineElementString )
        
        self.assertAlmostEqual( myTwoLineElement.__repr__(), twoLineElementString )


if __name__ == '__main__':
    unittest.main()