#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from event import Event

import unittest


date = "Jul 05"
description = "description"

eventString = date + " | " + description


class Test( unittest.TestCase ):

    def testEvent( self ):

        myEvent = Event( date, description )
        self.assertAlmostEqual( myEvent.getDate(), date )
        self.assertAlmostEqual( myEvent.getDescription(), description )

        self.assertAlmostEqual( myEvent.__eq__( Event( date, description ) ), True )
        self.assertAlmostEqual( myEvent.__eq__( Event( date + " ", description ) ), False )
        self.assertAlmostEqual( myEvent.__eq__( Event( date, description + " " ) ), False )

        self.assertAlmostEqual( myEvent.__str__(), eventString )

        self.assertAlmostEqual( myEvent.__repr__(), eventString )


if __name__ == '__main__':
    unittest.main()