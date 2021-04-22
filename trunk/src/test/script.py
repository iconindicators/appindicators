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
    # Working/starting directory.
    # Terminal open - If True, the terminal used to run the script will be left open at the end of script/command execution.
#
#TODO Document all parameters.
#
#TODO Figure out which parameters apply to both passive/background and active scripts and put those first.
# Then after the runInBackgroudFlag list the attributes for active scripts first followed by the background attributes.
# Or, can we have two factory methods and a hidden constructor?
# https://www.geeksforgeeks.org/what-is-a-clean-pythonic-way-to-have-multiple-constructors-in-python/
# https://stackoverflow.com/questions/44726196/how-to-implement-multiple-constructors-in-python
# https://stackoverflow.com/questions/44765482/multiple-constructors-the-pythonic-way
    def __init__( self, group, name, command, directory = "", runInBackground = False, terminalOpen = False, playSound = False, showNotification = False ):
        self.group = group
        self.name = name
        self.command = command
        self.directory = directory
        self.runInBackground = runInBackground
        self.terminalOpen = terminalOpen
        self.playSound = playSound
        self.showNotification = showNotification


    def getGroup( self ): return self.group


    def getName( self ): return self.name


    def getCommand( self ): return self.command


    def getDirectory( self ): return self.directory


    def getRunInBackground( self ): return self.runInBackground


    def getTerminalOpen( self ): return self.terminalOpen


    def getPlaySound( self ): return self.playSound


    def getShowNotification( self ): return self.showNotification


    def isIdentical( self, script ):
        return self.group == script.getGroup() and \
               self.name == script.getName() and \
               self.command == script.getCommand() and \
               self.directory == script.getDirectory() and \
               self.background == script.getRunInBackground() and \
               self.terminalOpen == script.getTerminalOpen() and \
               self.playSound == script.getPlaySound() and \
               self.showNotification == script.getShowNotification()


    def __str__( self ):
        return self.getGroup() + " | " + \
               self.getName() + " | " + \
               self.getCommand() + " | " + \
               self.getDirectory() + " | " + \
               str( self.getRunInBackground() ) + " | " + \
               str( self.getTerminalOpen() ) + " | " + \
               str( self.getPlaySound() ) + " | " + \
               str( self.getShowNotification() )


    def __repr__( self ): return self.__str__()