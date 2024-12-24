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


'''
Script information.

Base class encapsulating basic script information.
Implementation classes for background and non-background scripts.
'''


from abc import ABC


class Info( ABC ):
    ''' Base class for script information. '''

    def __init__( self, group, name, command, play_sound, show_notification ):
        '''
        Group to which a script belongs.
        Name of script.
        The command or script with any arguments as needed.
        True to play a sound on completion of script/command execution.
        True to show a notification on completion of script/command execution.
        '''
        self.group = group
        self.name = name
        self.command = command
        self.play_sound = play_sound
        self.show_notification = show_notification


    def get_group( self ):
        return self.group


    def get_name( self ):
        return self.name


    def get_command( self ):
        return self.command


    def get_play_sound( self ):
        return self.play_sound


    def get_show_notification( self ):
        return self.show_notification


    def __eq__( self, other ):
        return \
            self.__class__ == other.__class__ and \
            self.get_group() == other.get_group() and \
            self.get_name() == other.get_name() and \
            self.get_command() == other.get_command() and \
            self.get_play_sound() == other.get_play_sound() and \
            self.get_show_notification() == other.get_show_notification()


#TODO Check this works.
    def __str__( self ):
        return (
            self.group + " | " +
            self.name + " | " +
            self.command + " | " +
            str( self.play_sound ) + " | " +
            str( self.show_notification ) )


    def __repr__( self ):
        return self.__str__()


class Background( Info ):
    ''' Background script information. '''

    def __init__(
            self,
            group,
            name,
            command,
            play_sound,
            show_notification,
            interval_in_minutes,
            force_update ):
        '''
        Group to which a script belongs.
        Name of script.
        The command or script with any arguments as needed.
        True to play a sound on completion of script/command execution.
        True to show a notification on completion of script/command execution.
        Update interval (in minutes).
        Force update; script will update on the next update for ANY background script.        
        '''
        super().__init__( group, name, command, play_sound, show_notification )
        self.interval_in_minutes = interval_in_minutes
        self.force_update = force_update


    def get_interval_in_minutes( self ):
        return int( self.interval_in_minutes )


    def get_force_update( self ):
        return self.force_update


    def __eq__( self, other ):
        return \
            super().__eq__( other ) and \
            self.__class__ == other.__class__ and \
            self.get_interval_in_minutes() == other.get_interval_in_minutes() and \
            self.get_force_update() == other.get_force_update()


#TODO Check this works.
    def __str__( self ):
        return (
            super().__str__() + " | " +
            str( self.interval_in_minutes ) + " | " +
            str( self.force_update ) )


    def __repr__( self ):
        return self.__str__()


class NonBackground( Info ):
    ''' Non-background (foreground) script information. '''

    def __init__(
            self,
            group,
            name,
            command,
            play_sound,
            show_notification,
            terminal_open,
            default ):
        '''
        Group to which a script belongs.
        Name of script.
        The command or script with any arguments as needed.
        True to play a sound on completion of script/command execution.
        True to show a notification on completion of script/command execution.
        True to leave the terminal open on completion of script/command execution.
        True if the script is default (only one non-background script can be default).
        '''
        super().__init__( group, name, command, play_sound, show_notification )
        self.terminal_open = terminal_open
        self.default = default


    def get_terminal_open( self ):
        return self.terminal_open


    def get_default( self ):
        return self.default


    def __eq__( self, other ):
        return \
            super().__eq__( other ) and \
            self.__class__ == other.__class__ and \
            self.get_terminal_open() == other.get_terminal_open() and \
            self.get_default() == other.get_default()


#TODO Check this works.
    def __str__( self ):
        return (
            super().__str__() + " | " +
            str( self.terminal_open ) + " | " +
            str( self.default ) )


    def __repr__( self ):
        return self.__str__()
