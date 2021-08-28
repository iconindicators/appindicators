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
# A base class encapsulates basic script information.
# Implementation classes hold attributes for background script and non-background scripts.


from abc import ABC


#TODO Do we store in JSON scripts in one list?  
# If so, need a flag per script now to discrimatate background from non-background...!
#
# Otherwise, have a separate list for each type.
#
# Also, maybe have a method which produces the text output of a script suitable for passing to JSON?
# Can/should the reverse be done?  Take a string list from JSON and easily create a script?
#
# So each of Background and NonBackground could have 
#    A function toList() which dumps to a list for saving out to JSON
#    A static function fromList() which takes a list (from JSON) and creates the script object. 

class Info( ABC ):

    # Create a script (neither background nor non-background).
    #
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


#TODO Test  See the PPA class...I use __eq__ there ...should I use this instead?
    def isIdentical( self, script ):
        return self.group == script.getGroup() and \
               self.name == script.getName() and \
               self.command == script.getCommand() and \
               self.playSound == script.getPlaySound() and \
               self.showNotification == script.getShowNotification()


#TODO Test
    def __str__( self ):
        return self.getGroup() + " | " + \
               self.getName() + " | " + \
               self.getCommand() + " | " + \
               str( self.getPlaySound() ) + " | " + \
               str( self.getShowNotification() )


#TODO Test
    def __repr__( self ): return self.__str__()


class Background( Info ):

    # Create a background script.
    #
    # Group to which a script belongs.
    # Name of script.
    # The command or script with any arguments as needed.
    # True to play a sound on completion of script/command execution.
    # True to show a notification on completion of script/command execution.
    # Update interval (in minutes).
    def __init__( self, group, name, command, playSound, showNotification, intervalInMinutes ):
        super().__init__( group, name, command, playSound, showNotification )
        self.intervalInMinutes = intervalInMinutes


    def getIntervalInMinutes( self ): return int( self.intervalInMinutes )


#TODO Test
    def __eq__( self, script ): 
        return super().isIdentical( script ) and \
               self.intervalInMinutes == script.getIntervalInMinutes()


#TODO Test
    def __str__( self ):
        return super().__str__() + " | " + \
               str( self.getIntervalInMinutes() )


#TODO Test...can we remove this and rely on the parent class?
    def __repr__( self ): return self.__str__()


class NonBackground( Info ):

    # Create a non-background script.
    #
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


#TODO Test
    def __eq__( self, script ): 
        return super().isIdentical( script ) and \
               self.terminalOpen == script.getTerminalOpen() and \
               self.default == script.getDefault()

#TODO Test
    def __str__( self ):
        return super().__str__() + " | " + \
               str( self.getTerminalOpen() ) + " | " + \
               str( self.getDefault() )


#TODO Test...can we remove this and rely on the parent class?
    def __repr__( self ): return self.__str__()