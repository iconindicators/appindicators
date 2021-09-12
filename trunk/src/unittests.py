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


if __name__ == '__main__':
    unittest.main()