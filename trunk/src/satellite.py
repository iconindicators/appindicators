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


# Two-line Element Set.
# http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/SSOP_Help/tle_def.html
# http://www.satobs.org/element.html
# http://en.wikipedia.org/wiki/Two-line_element_set
# https://www.mmto.org/obscats/tle.html
# http://celestrak.com/columns/v04n03


class SatelliteType: Debris, Platform, RocketBooster, Unknown = range( 4 )


class TLE:
    def __init__( self, tleTitle, tleLine1, tleLine2 ):
        self.tleTitle = tleTitle
        self.tleLine1 = tleLine1
        self.tleLine2 = tleLine2


    def getTLETitle( self ): return self.tleTitle


    def getTLELine1( self ): return self.tleLine1


    def getTLELine2( self ): return self.tleLine2


    def getName( self ): return self.tleTitle


    def getNumber( self ): return self.tleLine1[ 2 : 7 ]


    def getInternationalDesignator( self ): 
        launchYear = self.tleLine1[ 9 : 11 ]
        if int( launchYear ) < 57:
            launchYear = "20" + launchYear
        else:
            launchYear = "19" + launchYear 

        return launchYear + "-" + self.tleLine1[ 11 : 17 ].strip()


    def getType( self ):
        satelliteType = SatelliteType.Unknown
        if "DEB" in self.getName().upper():
            satelliteType = SatelliteType.Debris
        elif "PLAT" in self.getName().upper():
            satelliteType = SatelliteType.Platform
        elif "R/B" in self.getName().upper():
            satelliteType = SatelliteType.RocketBooster

        return satelliteType


    def __str__( self ): return str( self.tleTitle ) + " | " + str( self.tleLine1 ) + " | " + str( self.tleLine2 )


    def __repr__( self ): return self.__str__()