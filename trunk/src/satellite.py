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


from urllib.request import urlopen


#TODO Maybe rename the file to twolineelement (because we have a file called orbitalelement)?
#Naming the file satellite is fine but what to name the equivalent for comets and minor planets?
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


    def __str__( self ): return str( self.tleTitle ) + " | " + str( self.tleLine1 ) + " | " + str( self.tleLine2 )


    def __repr__( self ): return self.__str__()


# Downloads TLE data from the URL.
#
# On success, returns a dict:
#    Key: ( satellite name, satellite number ) ;
#    Value: satellite.TLE object.
#
# On error, may write to the log (if not None) and returns None.
def download( url, logging = None ):
    try:
        tleData = { }
        data = urlopen( url ).read().decode( "utf8" ).splitlines()
        for i in range( 0, len( data ), 3 ):
            tle = TLE( data[ i ].strip(), data[ i + 1 ].strip(), data[ i + 2 ].strip() )
            tleData[ ( tle.getName().upper(), tle.getNumber() ) ] = tle

    except Exception as e:
        tleData = None
        if logging is not None:
            logging.exception( e )
            logging.error( "Error retrieving satellite TLE data from " + str( url ) )

    return tleData