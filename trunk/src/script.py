#! /usr/bin/python3
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
    def __init__( self, group, name, command, terminalOpen, playSound, showNotification ):
        self.group = group
        self.name = name
        self.command = command
        self.terminalOpen = terminalOpen
        self.playSound = playSound
        self.showNotification = showNotification


    def getGroup( self ): return self.group


    def getName( self ): return self.name


    def getCommand( self ): return self.command


    def getTerminalOpen( self ): return self.terminalOpen


    def getPlaySound( self ): return self.playSound


    def getShowNotification( self ): return self.showNotification


    def isIdentical( self, script ):
        return self.group == script.getGroup() and \
               self.name == script.getName() and \
               self.command == script.getCommand() and \
               self.terminalOpen == script.getTerminalOpen() and \
               self.playSound == script.getPlaySound() and \
               self.showNotification == script.getShowNotification()


    def __str__( self ):
        return self.getGroup() + " | " + \
               self.getName() + " | " + \
               self.getCommand() + " | " + \
               str( self.getTerminalOpen() ) + " | " + \
               str( self.getPlaySound() ) + " | " + \
               str( self.getShowNotification() )


    def __repr__( self ): return self.__str__()