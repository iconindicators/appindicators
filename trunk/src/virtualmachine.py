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


# Virtual Machine information.


class Info:

    # Name of VM or Group (when group contains the full group hierarchy).
    # Boolean True if a group; False otherwise.
    # UUID of VM/Group.
    # Numeric amount to indent when groups are used. 
    def __init__( self, name, group, uuid, indent ):
        self.name = name
        self.group = group
        self.uuid = uuid
        self.indent = indent
        self.isRunning = False
        self.autoStart = False
        self.startCommand = "VBoxManage startvm %VM%"


    def getName( self ): return self.name


    def setName( self, name ): self.name = name


    def getStartCommand( self ): return self.startCommand


    def setStartCommand( self, startCommand ): self.startCommand = startCommand


    def getAutoStart( self ): return self.autoStart


    def setAutoStart( self, autoStart ): self.autoStart = autoStart


    def isGroup( self ): return self.group


    def getUUID( self ): return self.uuid


    def getIndent( self ): return self.indent


    def setRunning( self ): self.isRunning = True


    def isRunning( self ): return self.isRunning


    def __str__( self ): return self.getName() + " | " + str( self.isGroup() ) + " | " + self.getUUID()


    def __repr__( self ): return self.__str__()