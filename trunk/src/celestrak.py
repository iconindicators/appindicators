#!/usr/bin/env python3


# Test file to determine how many of the satellites et al from Celestrak (visual, weather, ... all)
# are rocket booster, debris, platform, payload or unknown by looking at the full text database from Celestrak.
# Requires downloading the full text database (satcat).
# Requires all the TLE files for all satellites, etc and combined (cat) into one file.


from urllib.request import urlopen
import satellite


def getSatelliteTLEData( url ):
    satelliteTLEData = { } # Key: ( satellite name, satellite number ) ; Value: satellite.TLE object.
    data = urlopen( url ).read().decode( "utf8" ).splitlines()
    for i in range( 0, len( data ), 3 ):
        tle = satellite.TLE( data[ i ].strip(), data[ i + 1 ].strip(), data[ i + 2 ].strip() )
        satelliteTLEData[ ( tle.getName(), tle.getNumber() ) ] = tle

    return satelliteTLEData


def getSatCat():
    satCat = { } # Key: Norad number; Value: data line.
    f = open( "/home/bernard/Desktop/satcat.txt", "r" )
    for line in f:
        noradNumber = line[ 13 : 18 ]
        satCat[ noradNumber ] = line
        
    return satCat


satCat = getSatCat()
# satelliteTLEData = getSatelliteTLEData( "http://celestrak.com/NORAD/elements/visual.txt" )
satelliteTLEData = getSatelliteTLEData( "file:///home/bernard/Desktop/celestrak.txt" )
unknowns = [ ]
rb = 0
deb = 0
plat = 0
pay = 0
for key in satelliteTLEData:
    name = satelliteTLEData.get( key ).getName()
    number = satelliteTLEData.get( key ).getNumber()
    internationalDesignator = satelliteTLEData.get( key ).getInternationalDesignator()
    
    if "R/B" in name.upper():
        rb += 1
        continue

    if "DEB" in name.upper():
        deb += 1
        continue

    if "PLAT" in name.upper():
        plat += 1
        continue

    payload = satCat[ number ][ 20 ]
    if "*" in payload:
        pay += 1
        continue

    unknowns.append( name )

print( "SatCat size", len( satCat ) )
print( "Master size", len( satelliteTLEData ) )
print( "R/B", rb )
print( "DEB", deb )
print( "PLAT", plat )
print( "PAYLOAD", pay )
print( "Unknowns", unknowns )
