#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from script import Info, Background, NonBackground

import unittest


group = "myGroup"
name = "myName"
command = "myCommand"
playSound = True
showNotification = False

string = group + " | " + name + " | " + command + " | " + str( playSound ) + " | " + str( showNotification )


class TestScript( unittest.TestCase ):

    def testInfo( self ):

        myScript = Info( group, name, command, playSound, showNotification )

        self.assertAlmostEqual( myScript.getGroup(), group )
        self.assertAlmostEqual( myScript.getName(), name )
        self.assertAlmostEqual( myScript.getCommand(), command )
        self.assertAlmostEqual( myScript.getPlaySound(), playSound )
        self.assertAlmostEqual( myScript.getShowNotification(), showNotification )

        self.assertAlmostEqual( myScript.__eq__( Info( group, name, command, playSound, showNotification ) ), True )
        self.assertAlmostEqual( myScript.__eq__( Info( group + " ", name, command, playSound, showNotification ) ), False )
        self.assertAlmostEqual( myScript.__eq__( Info( group, name + " ", command, playSound, showNotification ) ), False )
        self.assertAlmostEqual( myScript.__eq__( Info( group, name, command + " ", playSound, showNotification ) ), False )
        self.assertAlmostEqual( myScript.__eq__( Info( group, name, command, not playSound, showNotification ) ), False )
        self.assertAlmostEqual( myScript.__eq__( Info( group, name, command, playSound, not showNotification ) ), False )

        self.assertAlmostEqual( myScript.__str__(), string )

        self.assertAlmostEqual( myScript.__repr__(), string )


    def testBackground( self ):
        intervalInMinutes = 60

        myScript = Background( group, name, command, playSound, showNotification, intervalInMinutes )

        self.assertAlmostEqual( myScript.getGroup(), group )
        self.assertAlmostEqual( myScript.getName(), name )
        self.assertAlmostEqual( myScript.getCommand(), command )
        self.assertAlmostEqual( myScript.getPlaySound(), playSound )
        self.assertAlmostEqual( myScript.getShowNotification(), showNotification )
        self.assertAlmostEqual( myScript.getIntervalInMinutes(), intervalInMinutes )

        self.assertAlmostEqual( myScript.__eq__( Background( group, name, command, playSound, showNotification, intervalInMinutes ) ), True )
        self.assertAlmostEqual( myScript.__eq__( Background( group + " ", name, command, playSound, showNotification, intervalInMinutes ) ), False )
        self.assertAlmostEqual( myScript.__eq__( Background( group, name + " ", command, playSound, showNotification, intervalInMinutes ) ), False )
        self.assertAlmostEqual( myScript.__eq__( Background( group, name, command + " ", playSound, showNotification, intervalInMinutes ) ), False )
        self.assertAlmostEqual( myScript.__eq__( Background( group, name, command, not playSound, showNotification, intervalInMinutes ) ), False )
        self.assertAlmostEqual( myScript.__eq__( Background( group, name, command, playSound, not showNotification, intervalInMinutes ) ), False )
        self.assertAlmostEqual( myScript.__eq__( Background( group, name, command, playSound, showNotification, 120 ) ), False )

        self.assertAlmostEqual( myScript.__str__(), string + " | " + str( intervalInMinutes ) )

        self.assertAlmostEqual( myScript.__repr__(), string + " | " + str( intervalInMinutes ) )


    def testNonBackground( self ):
        terminalOpen = True
        default = True

        myScript = NonBackground( group, name, command, playSound, showNotification, terminalOpen, default )

        self.assertAlmostEqual( myScript.getGroup(), group )
        self.assertAlmostEqual( myScript.getName(), name )
        self.assertAlmostEqual( myScript.getCommand(), command )
        self.assertAlmostEqual( myScript.getPlaySound(), playSound )
        self.assertAlmostEqual( myScript.getShowNotification(), showNotification )
        self.assertAlmostEqual( myScript.getTerminalOpen(), terminalOpen )
        self.assertAlmostEqual( myScript.getDefault(), default )

        self.assertAlmostEqual( myScript.__eq__( NonBackground( group, name, command, playSound, showNotification, terminalOpen, default ) ), True )
        self.assertAlmostEqual( myScript.__eq__( NonBackground( group + " ", name, command, playSound, showNotification, terminalOpen, default ) ), False )
        self.assertAlmostEqual( myScript.__eq__( NonBackground( group, name + " ", command, playSound, showNotification, terminalOpen, default ) ), False )
        self.assertAlmostEqual( myScript.__eq__( NonBackground( group, name, command + " ", playSound, showNotification, terminalOpen, default ) ), False )
        self.assertAlmostEqual( myScript.__eq__( NonBackground( group, name, command, not playSound, showNotification, terminalOpen, default ) ), False )
        self.assertAlmostEqual( myScript.__eq__( NonBackground( group, name, command, playSound, not showNotification, terminalOpen, default ) ), False )
        self.assertAlmostEqual( myScript.__eq__( NonBackground( group, name, command, playSound, showNotification, not terminalOpen, default ) ), False )
        self.assertAlmostEqual( myScript.__eq__( NonBackground( group, name, command, playSound, showNotification, terminalOpen, not default ) ), False )

        self.assertAlmostEqual( myScript.__str__(), string + " | " + str( terminalOpen ) + " | " + str( default ) )

        self.assertAlmostEqual( myScript.__repr__(), string + " | " + str( terminalOpen ) + " | " + str( default ) )


if __name__ == '__main__':
    unittest.main()