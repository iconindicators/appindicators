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
#TODO Document all parameters.
    def __init__( self, group, name, command, directory = "", background = False, terminalOpen = False, playSound = False, showNotification = False ):
        self.group = group
        self.name = name
        self.command = command
        self.directory = directory
        self.background = background
        self.terminalOpen = terminalOpen
        self.playSound = playSound
        self.showNotification = showNotification


    def getGroup( self ): return self.group


    def getName( self ): return self.name


    def getCommand( self ): return self.command


    def getDirectory( self ): return self.directory


    def isBackground( self ): return self.background


    def isTerminalOpen( self ): return self.terminalOpen


    def playSound( self ): return self.playSound


    def showNotification( self ): return self.showNotification


    def isIdentical( self, script ):
        return self.group == script.getGroup() and \
               self.name == script.getName() and \
               self.command == script.getCommand() and \
               self.directory == script.getDirectory() and \
               self.background == script.isBackground() and \
               self.terminalOpen == script.isTerminalOpen() and \
               self.playSound == script.playSound() and \
               self.showNotification == script.showNotification()


    def __str__( self ):
        return self.getGroup() + " | " + \
               self.getName() + " | " + \
               self.getCommand() + " | " + \
               self.getDirectory() + " | " + \
               str( self.isBackground() ) + " | " + \
               str( self.isTerminalOpen() ) + " | " + \
               str( self.playSound() ) + " | " + \
               str( self.showNotification() )


    def __repr__( self ): return self.__str__()