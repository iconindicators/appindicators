#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from virtualmachine import Group, VirtualMachine

import unittest


name = "name"
uuid = "uuid"


class Test( unittest.TestCase ):

    def testVirtualMachine( self ):
        virtualMachineString = name + " | " + uuid

        myVirtualMachine = VirtualMachine( name, uuid )
        self.assertAlmostEqual( myVirtualMachine.getName(), name )
        self.assertAlmostEqual( myVirtualMachine.getUUID(), uuid )

        self.assertAlmostEqual( myVirtualMachine.__eq__( VirtualMachine( name, uuid ) ), True )
        self.assertAlmostEqual( myVirtualMachine.__eq__( VirtualMachine( name + " ", uuid ) ), False )
        self.assertAlmostEqual( myVirtualMachine.__eq__( VirtualMachine( name , uuid + " " ) ), False )

        self.assertAlmostEqual( myVirtualMachine.__str__(), virtualMachineString )

        self.assertAlmostEqual( myVirtualMachine.__repr__(), virtualMachineString )


    def testGroup( self ):
        myGroup = Group( name )
        groupString = name + ": "

        self.assertAlmostEqual( myGroup.getName(), name )

        self.assertAlmostEqual( myGroup.__eq__( Group( name ) ), True )
        self.assertAlmostEqual( myGroup.__eq__( Group( name + " " ) ), False )

        self.assertAlmostEqual( myGroup.__str__(), groupString )
        
        self.assertAlmostEqual( myGroup.__repr__(), groupString )


    def testGroupItems( self ):
        myGroup = Group( name )
        myGroup.addItem( VirtualMachine( name, uuid ) )
        myGroup.addItem( Group( name ) )
        myGroup.getItems()[ -1 ].addItem( VirtualMachine( name, uuid ) )

        self.assertAlmostEqual( myGroup.getName(), name )

        self.assertAlmostEqual( myGroup.__eq__( Group( name ) ), False )

        myOtherGroup = Group( name )
        myOtherGroup.addItem( Group( name ) )
        myOtherGroup.getItems()[ -1 ].addItem( VirtualMachine( name, uuid ) )
        myOtherGroup.addItem( VirtualMachine( name, uuid ) )

        self.assertAlmostEqual( myGroup.__eq__( myOtherGroup ), False )

        myOtherGroup = Group( name )
        myOtherGroup.addItem( VirtualMachine( name, uuid ) )
        myOtherGroup.addItem( Group( name ) )
        myOtherGroup.getItems()[ -1 ].addItem( VirtualMachine( name, uuid ) )

        self.assertAlmostEqual( myGroup.__eq__( myOtherGroup ), True )

        groupString = name + ": " + name + " | " + name

        self.assertAlmostEqual( myGroup.__str__(), groupString )

        self.assertAlmostEqual( myGroup.__repr__(), groupString )


if __name__ == '__main__':
    unittest.main()