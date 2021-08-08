#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


# Script information.


class Info( object ):

    # Group to which a script belongs.
    # Name of script.
    # The command or script with any arguments as needed.
    # Leave the terminal (used to execute the script/command) open on completion.
    # Play a sound on completion of script/command execution.
    # Show a notification on completion of script/command execution.
    # Is a script background (displays result in a label) versus a foreground script (activated by user).
    # Update interval for a background script (ignored for foreground scripts).
#TODO Figure out which parameters apply to both passive/background and active scripts and put those first.
# Then after the runInBackgroudFlag list the attributes for active scripts first followed by the background attributes.
# Or, use two factory methods (classmethods) and just don't use the constructor.
# https://www.geeksforgeeks.org/what-is-a-clean-pythonic-way-to-have-multiple-constructors-in-python/
# https://stackoverflow.com/questions/44726196/how-to-implement-multiple-constructors-in-python
# https://stackoverflow.com/questions/44765482/multiple-constructors-the-pythonic-way
# If the attributes of terminalOpen, playSound and showNotification ultimately also apply to background scripts,
# move the runInBackgroud parameter to just before intervalInMinutes.
    def __init__( self, group, name, command, terminalOpen, playSound, showNotification, background, intervalInMinutes ):
        self.group = group
        self.name = name
        self.command = command

        # Apply only to foreground scripts.  TODO Is this still correct?
        self.terminalOpen = terminalOpen #TODO Apply also somehow to background scripts?
        self.playSound = playSound #TODO Ditto
        self.showNotification = showNotification #TODO Ditto

        self.background = background

        # Apply only to background scripts.
        self.intervalInMinutes = intervalInMinutes #TODO Document/decide if this is to be an int or str.


#TODO Probably not needed.
    # @classmethod
    # def foregroundScript( cls, group, name, command, directory, terminalOpen = False, playSound = False, showNotification = False ):
        # return cls( group, name, command, directory, False, terminalOpen, playSound, showNotification )


    # @classmethod
    # def backgroundScript( cls, group, name, command, intervalInMinutes = 60 ):
        # return cls( group, name, command, None, True, False, False, False, intervalInMinutes )


    def getGroup( self ): return self.group


    def getName( self ): return self.name


    def getCommand( self ): return self.command


    def getTerminalOpen( self ): return self.terminalOpen


    def getPlaySound( self ): return self.playSound


    def getShowNotification( self ): return self.showNotification


    def getBackground( self ): return self.background


    def getIntervalInMinutes( self ): return str( self.intervalInMinutes )


#TODO Add stuff for background scripts.
# Will need to check first if a script is background or not?  Or just compare all attributes?
    def isIdentical( self, script ):
        return self.group == script.getGroup() and \
               self.name == script.getName() and \
               self.command == script.getCommand() and \
               self.terminalOpen == script.getTerminalOpen() and \
               self.playSound == script.getPlaySound() and \
               self.showNotification == script.getShowNotification()


#TODO Add stuff for background scripts.
# Will need to check first if a script is background or not?  Or just print/return all attributes?
    def __str__( self ):
        return self.getGroup() + " | " + \
               self.getName() + " | " + \
               self.getCommand() + " | " + \
               str( self.getTerminalOpen() ) + " | " + \
               str( self.getPlaySound() ) + " | " + \
               str( self.getShowNotification() )


    def __repr__( self ): return self.__str__()