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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# Script information.


class Info( object ):

    # Group to which a script belongs.
    # Name of script.
    # Working/starting directory (may be "").
    # The command or script with any arguments as needed.
    # Boolean - If True, the terminal used to run the script will be left open at the end of script/command execution.
    def __init__( self, group, name, directory, command, terminalOpen ):
        self.group = group
        self.name = name
        self.directory = directory
        self.command = command
        self.terminalOpen = terminalOpen
        self.playSound = False
        self.showNotification = False


    def getGroup( self ): return self.group


    def getName( self ): return self.name


    def getDirectory( self ): return self.directory


    def getCommand( self ): return self.command


    def getPlaySound( self ): return self.playSound


    def setPlaySound( self, playSound ): self.playSound = playSound


    def getShowNotification( self ): return self.showNotification


    def setShowNotification( self, showNotification ): self.showNotification = showNotification


    def isTerminalOpen( self ): return self.terminalOpen


    def isIdentical( self, script ):
        return self.group == script.getGroup() and \
               self.name == script.getName() and \
               self.directory == script.getDirectory() and \
               self.command == script.getCommand() and \
               self.terminalOpen == script.isTerminalOpen() and \
               self.playSound == script.getPlaySound() and \
               self.showNotification == script.getShowNotification()


    def __str__( self ):
        return self.getGroup() + " | " + \
               self.getName() + " | " + \
               self.getDirectory() + " | " + \
               self.getCommand() + " | " + \
               str( self.isTerminalOpen() ) + " | " + \
               str( self.getPlaySound() ) + " | " + \
               str( self.getShowNotification() )


    def __repr__( self ): return self.__str__()