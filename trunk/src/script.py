#!/usr/bin/env python3


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


class Info:

    # Name of script.
    # Description of script.
    # Working/starting directory (may be "").
    # The command or script with any arguments as needed.
    # Boolean - If True, the terminal used to run the script will be left open at the end of script/command execution.
    def __init__( self, name, description, directory, command, terminalOpen ):
        self.name = name
        self.description = description
        self.directory = directory
        self.command = command
        self.terminalOpen = terminalOpen


    def getName( self ): return self.name


    def getDescription( self ): return self.description


    def getDirectory( self ): return self.directory


    def getCommand( self ): return self.command


    def isTerminalOpen( self ): return self.terminalOpen


    def isIdentical( self, script ):
        return self.name == script.getName() and \
               self.description == script.getDescription() and \
               self.directory == script.getDirectory() and \
               self.command == script.getCommand() and \
               self.terminalOpen == script.isTerminalOpen()


    def __str__( self ): return self.getName() + " | " + self.getDescription() + " | " + self.getDirectory() + " | " + self.getCommand() + " | " + str( self.isTerminalOpen() )


    def __repr__( self ): return self.__str__()