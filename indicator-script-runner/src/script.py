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
#
# Base class encapsulating basic script information.
# Implementation classes for background and non-background scripts.


from abc import ABC


class Info( ABC ):

    # Group to which a script belongs.
    # Name of script.
    # The command or script with any arguments as needed.
    # True to play a sound on completion of script/command execution.
    # True to show a notification on completion of script/command execution.
    def __init__( self, group, name, command, playSound, showNotification ):
        self.group = group
        self.name = name
        self.command = command
        self.playSound = playSound
        self.showNotification = showNotification


    def getGroup( self ): return self.group


    def getName( self ): return self.name


    def getCommand( self ): return self.command


    def getPlaySound( self ): return self.playSound


    def getShowNotification( self ): return self.showNotification


    def __eq__( self, other ): 
        return \
            self.__class__ == other.__class__ and \
            self.getGroup() == other.getGroup() and \
            self.getName() == other.getName() and \
            self.getCommand() == other.getCommand() and \
            self.getPlaySound() == other.getPlaySound() and \
            self.getShowNotification() == other.getShowNotification()


    def __str__( self ):
        return \
            self.group + " | " + \
            self.name + " | " + \
            self.command + " | " + \
            str( self.playSound ) + " | " + \
            str( self.showNotification )


    def __repr__( self ): return self.__str__()


class Background( Info ):

    # Group to which a script belongs.
    # Name of script.
    # The command or script with any arguments as needed.
    # True to play a sound on completion of script/command execution.
    # True to show a notification on completion of script/command execution.
    # Update interval (in minutes).
    # Force update; script will update when the next update occurs for ANY background script.
    def __init__( self, group, name, command, playSound, showNotification, intervalInMinutes, forceUpdate ):
        super().__init__( group, name, command, playSound, showNotification )
        self.intervalInMinutes = intervalInMinutes
        self.forceUpdate = forceUpdate


    def getIntervalInMinutes( self ): return int( self.intervalInMinutes )


    def getForceUpdate( self ): return self.forceUpdate


    def __eq__( self, other ): 
        return \
            super().__eq__( other ) and \
            self.__class__ == other.__class__ and \
            self.getIntervalInMinutes() == other.getIntervalInMinutes() and \
            self.getForceUpdate() == other.getForceUpdate()


    def __str__( self ):
        return \
            super().__str__() + " | " + \
            str( self.intervalInMinutes ) + " | " + \
            str( self.forceUpdate )


    def __repr__( self ): return self.__str__()


class NonBackground( Info ):

    # Group to which a script belongs.
    # Name of script.
    # The command or script with any arguments as needed.
    # True to play a sound on completion of script/command execution.
    # True to show a notification on completion of script/command execution.
    # True to leave the terminal open on completion of script/command execution.
    # True if the script is default (only one non-background script can be default).
    def __init__( self, group, name, command, playSound, showNotification, terminalOpen, default ):
        super().__init__( group, name, command, playSound, showNotification )
        self.terminalOpen = terminalOpen
        self.default = default


    def getTerminalOpen( self ): return self.terminalOpen


    def getDefault( self ): return self.default


    def __eq__( self, other ): 
        return \
            super().__eq__( other ) and \
            self.__class__ == other.__class__ and \
            self.getTerminalOpen() == other.getTerminalOpen() and \
            self.getDefault() == other.getDefault()


    def __str__( self ):
        return \
            super().__str__() + " | " + \
            str( self.terminalOpen ) + " | " + \
            str( self.default )


    def __repr__( self ): return self.__str__()